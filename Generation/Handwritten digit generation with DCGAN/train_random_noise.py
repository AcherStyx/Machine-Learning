from trainers.random_noise import Trainer
from configs.default import *


if __name__ == "__main__":
    from models.random_noise.dcgan_generator import DCGANGenerator
    from models.random_noise.dcgan_discriminator import DCGANDiscriminator
    from data_loaders.load_mnist import LoadMNIST

    trainer = Trainer(
        generator=DCGANGenerator(GeneratorConfig).get_model(),
        discriminator=DCGANDiscriminator().get_model(),
        data=LoadMNIST(DataLoaderConfig).get_dataset(),
        config=TrainerConfig,
    )

    trainer.train()
