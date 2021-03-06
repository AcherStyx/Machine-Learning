class ModelTemplate:
    def __init__(self, config):
        """
        init the models
        :param config: configs you want to use in `build` method
        """
        self.config = config
        self.model = None

    def load(self, checkpoint_path):
        """
        load models from file
        :param checkpoint_path: the path to the checkpoint file
        :return: None
        """
        if self.model is None:
            raise Exception("[Error] Build the models first.")

        self.model.load_weights(checkpoint_path)
        print("[Info] Model loaded.")

    def save(self, checkpoint_path):
        """
        save models to file
        :param checkpoint_path: the path to the checkpoint file
        :return:
        """
        if self.model is None:
            raise Exception("[Error] Build the models first.")

        self.model.save_weights(checkpoint_path)
        print("[Info] Model saved.")

    def build(self):
        """
        build the models here
        """
        raise NotImplementedError

    def get_model(self):
        if self.model is None:
            raise Exception("[Error] Build the models first.")

        return self.model
