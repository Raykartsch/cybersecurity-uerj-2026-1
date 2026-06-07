import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import os

# Set seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

def load_and_preprocess_data(file_path):
    print(f"Loading data from {file_path}...")
    df = pd.read_parquet(file_path)
    
    # Identify features and labels
    # Based on the dataset schema, 'Attack_label' is binary (0: normal, 1: attack)
    # 'Attack_type' is multiclass. We use 'Attack_label' for malign detection.
    target = 'Attack_label'
    
    # Columns to drop (IDs, timestamps, or high cardinality strings that might cause overfitting)
    drop_cols = [
        'frame.time', 'ip.src_host', 'ip.dst_host', 'http.request.uri.query', 
        'http.referer', 'http.request.full_uri', 'mqtt.msg', 'mqtt.topic', 
        'dns.qry.name', 'Attack_type'
    ]
    
    # Only drop if they exist in the dataframe
    drop_cols = [col for col in drop_cols if col in df.columns]
    df = df.drop(columns=drop_cols)
    
    # Handle missing values
    df = df.fillna(0)
    
    # Encode categorical columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
    
    X = df.drop(columns=[target])
    y = df[target]
    
    # Feature Scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y, X.columns

class DualContrastiveModel(models.Model):
    def __init__(self, encoder, num_classes, embedding_dim=64, temperature=0.07):
        super().__init__()
        self.encoder = encoder
        self.temperature = temperature
        # Classifier weights used as "label anchors" in DualCL
        self.classifier_weights = self.add_weight(
            shape=(num_classes, embedding_dim),
            initializer="glorot_uniform",
            trainable=True,
            name="classifier_weights"
        )
        self.loss_tracker = tf.keras.metrics.Mean(name="loss")
        self.acc_metric = tf.keras.metrics.SparseCategoricalAccuracy(name="accuracy")

    def call(self, x, training=False):
        features = self.encoder(x, training=training)
        # Normalize features and weights for cosine similarity
        features = tf.math.l2_normalize(features, axis=1)
        weights = tf.math.l2_normalize(self.classifier_weights, axis=0)
        # Classification via dot product (logits)
        logits = tf.matmul(features, weights, transpose_b=True) / self.temperature
        return logits

    def train_step(self, data):
        x, y = data

        with tf.GradientTape() as tape:
            # 1. Forward pass
            features = self.encoder(x, training=True)
            features = tf.math.l2_normalize(features, axis=1)
            weights = tf.math.l2_normalize(self.classifier_weights, axis=0)
            
            # 2. Similarity matrix (Sample-to-Label)
            logits = tf.matmul(features, weights, transpose_b=True) / self.temperature
            
            # 3. Standard Cross-Entropy (Feature-to-Classifier)
            loss_ce = tf.keras.losses.sparse_categorical_crossentropy(
                y, logits, from_logits=True
            )
            
            # 4. Dual Contrastive Component (Label-to-Sample)
            # Transpose to treat labels as anchors for the batch
            logits_dual = tf.transpose(logits)
            
            # Create mask for samples belonging to each class in the batch
            y_reshaped = tf.reshape(y, (-1,))
            num_classes = tf.shape(weights)[0]
            mask = tf.one_hot(tf.cast(y_reshaped, tf.int32), num_classes)
            mask = tf.transpose(mask) # (num_classes, batch_size)
            
            # Avoid division by zero for classes not in batch
            mask_sum = tf.reduce_sum(mask, axis=1, keepdims=True)
            mask = mask / tf.maximum(mask_sum, 1.0)
            
            # Log-Softmax over batch dimension for label-to-sample alignment
            log_prob = tf.nn.log_softmax(logits_dual, axis=1)
            loss_dual = -tf.reduce_sum(mask * log_prob, axis=1)
            
            # Combined Loss
            total_loss = tf.reduce_mean(loss_ce + loss_dual)

        # 5. Compute and apply gradients
        trainable_vars = self.trainable_variables
        gradients = tape.gradient(total_loss, trainable_vars)
        self.optimizer.apply_gradients(zip(gradients, trainable_vars))

        # 6. Update metrics
        self.loss_tracker.update_state(total_loss)
        self.acc_metric.update_state(y, logits)
        return {"loss": self.loss_tracker.result(), "accuracy": self.acc_metric.result()}

    def test_step(self, data):
        x, y = data
        logits = self(x, training=False)
        loss = tf.reduce_mean(tf.keras.losses.sparse_categorical_crossentropy(y, logits, from_logits=True))
        self.acc_metric.update_state(y, logits)
        return {"loss": loss, "accuracy": self.acc_metric.result()}

def build_cnn_encoder(input_shape, embedding_dim=64):
    encoder = models.Sequential([
        layers.Input(shape=input_shape),
        layers.Reshape((input_shape[0], 1)),
        
        layers.Conv1D(64, kernel_size=3, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        
        layers.Conv1D(128, kernel_size=3, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        
        layers.Flatten(),
        layers.Dense(embedding_dim),
    ])
    return encoder

def main():
    file_path = r"C:/Users/Italo/Desktop/UERJ/2026.1/cibersecurity/cybersecurity-uerj-2026-1/final-project/db/dnn.parquet"
    
    if not os.path.exists(file_path):
        file_path = "final-project/db/dnn.parquet"
    
    try:
        X, y, feature_names = load_and_preprocess_data(file_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Training data shape: {X_train.shape}")
    
    # Build model with Dual Contrastive Loss
    input_shape = (X_train.shape[1],)
    num_classes = 2 # Binary: Normal or Attack
    embedding_dim = 64
    
    encoder = build_cnn_encoder(input_shape, embedding_dim)
    model = DualContrastiveModel(encoder, num_classes, embedding_dim)
    
    model.compile(optimizer='adam')
    
    # Callbacks
    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    
    # Train
    print("Starting training with Dual Contrastive Loss...")
    model.fit(
        X_train, y_train,
        epochs=20,
        batch_size=1024,
        validation_data=(X_test, y_test),
        callbacks=[early_stopping],
        verbose=1
    )
    
    # Evaluate
    print("\nEvaluating model on test set...")
    metrics = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Accuracy: {metrics[1]:.4f}")
    
    # Save model (saving encoder as it's the main feature extractor)
    model_save_path = "final-project/traffic_cnn_encoder.h5"
    encoder.save(model_save_path)
    print(f"\nEncoder model saved to {model_save_path}")

if __name__ == "__main__":
    main()
