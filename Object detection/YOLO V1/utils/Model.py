import os
import tensorflow as tf
import tensorflow_hub as hub
import utils.Config as Config
from utils.YoloLoss import yolo_loss

os.environ["PATH"] += os.pathsep + "D:/graphviz/bin"
os.environ['TFHUB_CACHE_DIR'] = './.data/'


def yolo_model(model_type="TRANSFER", show_summary=False):
    """
    build neural network model for yolo
    @param model_type: "INCEPTION V3" or "ORIGINAL"
    @param show_summary: Show summary of the model
    @return: keras model
    """
    input_layer = tf.keras.Input(shape=(Config.ImageSize, Config.ImageSize, 3), name="input")

    hidden_layer = tf.keras.layers.Dropout(Config.Dropout_Image)(input_layer)

    # TODO: Model switch for different model
    if model_type == "INCEPTION V3":
        # Inception model from tfhub
        inception_feature_extractor = hub.keras_layer.KerasLayer(
            "https://storage.googleapis.com/tfhub-modules/google/tf2-preview/inception_v3/feature_vector/4.tar.gz",
            output_shape=[2048],
            trainable=False)
        # Follow layers
        hidden_layer = inception_feature_extractor(hidden_layer)
        hidden_layer = tf.keras.layers.Dropout(Config.Dropout_Output)(hidden_layer)
    elif model_type == "INCEPTION V3 KERAS":
        # load inception network to extract feature from the image
        inception_feature_extractor = tf.keras.applications.inception_v3.InceptionV3(include_top=False,
                                                                                     weights='imagenet',
                                                                                     input_tensor=hidden_layer,
                                                                                     input_shape=None,
                                                                                     pooling=None)
        # # don't train these params
        # for layers in inception_feature_extractor.layers[:]:
        #     layers.trainable = False

        # feature extractor
        hidden_layer = inception_feature_extractor.output
        # generate the output of the conventional network
        # without any dense layer
        with tf.device("/CPU:0"):
            hidden_layer = tf.keras.layers.GlobalAveragePooling2D()(hidden_layer)
            hidden_layer = tf.keras.layers.Dropout(Config.Dropout_Output)(hidden_layer)
            hidden_layer = tf.keras.layers.Flatten()(hidden_layer)
    elif model_type == "ORIGINAL":
        # period 1 - reduce image size
        hidden_layer = tf.keras.layers.Conv2D(filters=64,
                                              kernel_size=(7, 7),
                                              strides=(2, 2),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.MaxPool2D(pool_size=(2, 2),
                                                 strides=(2, 2),
                                                 padding="SAME",
                                                 )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=192,
                                              kernel_size=(3, 3),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.MaxPool2D(pool_size=(2, 2),
                                                 strides=(2, 2),
                                                 padding="SAME",
                                                 )(hidden_layer)

        # period 2 - increase deep
        hidden_layer = tf.keras.layers.Conv2D(filters=128,
                                              kernel_size=(1, 1),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=256,
                                              kernel_size=(3, 3),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=256,
                                              kernel_size=(1, 1),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=512,
                                              kernel_size=(3, 3),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.MaxPool2D(pool_size=(2, 2),
                                                 strides=(2, 2),
                                                 padding="SAME",
                                                 )(hidden_layer)

        # period 3
        hidden_layer = tf.keras.layers.Conv2D(filters=256,
                                              kernel_size=(1, 1),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=512,
                                              kernel_size=(3, 3),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=256,
                                              kernel_size=(1, 1),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=512,
                                              kernel_size=(3, 3),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=256,
                                              kernel_size=(1, 1),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=512,
                                              kernel_size=(3, 3),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=256,
                                              kernel_size=(1, 1),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=512,
                                              kernel_size=(3, 3),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=512,
                                              kernel_size=(1, 1),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=1024,
                                              kernel_size=(3, 3),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.MaxPool2D(pool_size=(2, 2),
                                                 strides=(2, 2),
                                                 padding="SAME",
                                                 )(hidden_layer)

        # period 4
        hidden_layer = tf.keras.layers.Conv2D(filters=512,
                                                     kernel_size=(1, 1),
                                                     padding="SAME",
                                                     kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                                     use_bias=False,
                                                     )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=1024,
                                                     kernel_size=(3, 3),
                                                     padding="SAME",
                                                     kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                                     use_bias=False,
                                                     )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=512,
                                                     kernel_size=(1, 1),
                                                     padding="SAME",
                                                     kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                                     use_bias=False,
                                                     )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=1024,
                                                     kernel_size=(3, 3),
                                                     padding="SAME",
                                                     kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                                     use_bias=False,
                                                     )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=1024,
                                              kernel_size=(3, 3),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=1024,
                                              kernel_size=(3, 3),
                                              strides=(2, 2),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False,
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        # period 5
        hidden_layer = tf.keras.layers.Conv2D(filters=1024,
                                              kernel_size=(3, 3),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.Conv2D(filters=1024,
                                              kernel_size=(3, 3),
                                              padding="SAME",
                                              kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                              use_bias=False
                                              )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
        hidden_layer = tf.keras.layers.MaxPool2D(pool_size=(7, 7),
                                                 strides=(1, 1),
                                                 padding="valid")(hidden_layer)
        hidden_layer = tf.keras.layers.Dropout(Config.Dropout_Output)(hidden_layer)
        hidden_layer = tf.keras.layers.Flatten()(hidden_layer)
        hidden_layer = tf.keras.layers.Dense(4096,
                                             kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                             )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(negative_slope=Config.ReLU_Slope)(hidden_layer)
    elif model_type == "XCEPTION":
        xception_feature_extractor = tf.keras.applications.xception.Xception(include_top=False,
                                                                             weights='imagenet',
                                                                             input_tensor=input_layer,
                                                                             pooling=None,
                                                                             classes=4096)
        hidden_layer = xception_feature_extractor(hidden_layer)
        hidden_layer = tf.keras.layers.Dropout(Config.Dropout_Output)(hidden_layer)
    else:
        raise TypeError

    # fully connected layers
    with tf.device("/CPU:0"):
        hidden_layer = tf.keras.layers.Dense(512,
                                             kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                             )(hidden_layer)
        hidden_layer = tf.keras.layers.ReLU(max_value=1)(hidden_layer)
        hidden_layer = tf.keras.layers.Dense(Config.CellSize * Config.CellSize * 30,
                                             kernel_initializer=tf.keras.initializers.TruncatedNormal(),
                                             )(hidden_layer)
        # # use linear activation in output layer
        # hidden_layer = tf.keras.layers.ReLU(max_value=1)(hidden_layer)

        # reshape the output to the shape of [CellSize, CellSize, 30]
        output = tf.keras.layers.Reshape((Config.CellSize,
                                          Config.CellSize,
                                          5 * Config.BoxPerCell + Config.ClassesNum),
                                         name="output")(hidden_layer)
    # get model by define the input and output
    net_model = tf.keras.Model(inputs=input_layer,
                               outputs=output,
                               name="Yolo_Model")
    # set compile method
    net_model.compile(optimizer=tf.keras.optimizers.SGD(Config.LearningRate, Config.Momentum, decay=Config.Decay),
                      loss=yolo_loss)
    # show summary in text
    net_model.summary()
    if show_summary:
        # show summary in flow chart
        tf.keras.utils.plot_model(model=net_model,
                                  to_file='Net.png',
                                  show_shapes=True,
                                  dpi=50)
    return net_model


if __name__ == "__main__":
    print("Is there a GPU available: ", tf.test.is_gpu_available())
    model = yolo_model(model_type="INCEPTION V3 KERAS", show_summary=True)
