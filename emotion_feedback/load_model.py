import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten
from tensorflow.keras.optimizers import Adam
import os

def create_model():
    model = Sequential([
        Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48, 48, 1)),
        Conv2D(64, kernel_size=(3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),
        
        Conv2D(128, kernel_size=(3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(128, kernel_size=(3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),
        
        Flatten(),
        Dense(1024, activation='relu'),
        Dropout(0.5),
        Dense(7, activation='softmax')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

if __name__ == '__main__':
    # Create and save the model
    model = create_model()
    
    # Load pre-trained weights if available
    model_path = os.path.join('models', 'emotion_model.h5')
    if os.path.exists(model_path):
        print("Loading existing model...")
        model.load_weights(model_path)
    else:
        print("Creating new model...")
        # Here we would normally train the model
        # For now, we'll just save the untrained model
        os.makedirs('models', exist_ok=True)
        model.save(model_path)
    
    print("Model ready!") 