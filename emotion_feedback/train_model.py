import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from load_model import create_model
import os

def train_emotion_model():
    # Create data generators
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    # Load and preprocess the data
    # Note: You need to organize your training data in directories named after emotions
    train_generator = train_datagen.flow_from_directory(
        'data/train',
        target_size=(48, 48),
        color_mode='grayscale',
        batch_size=32,
        class_mode='categorical'
    )

    # Create and compile the model
    model = create_model()

    # Train the model
    model.fit(
        train_generator,
        epochs=50,
        steps_per_epoch=len(train_generator),
        verbose=1
    )

    # Save the trained model
    model_path = os.path.join('models', 'emotion_model.h5')
    model.save(model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_emotion_model() 