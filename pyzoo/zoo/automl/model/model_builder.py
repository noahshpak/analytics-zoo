#
# Copyright 2018 Analytics Zoo Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either exp'
# ress or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


class ModelBuilder:
    def __init__(self, backend=None, cls=None, **params):
        self.params = params
        self.backend = backend
        self.cls = cls

    @classmethod
    def from_pytorch(cls, model_creator, optimizer_creator, loss_creator):
        return cls(backend="pytorch",
                   model_creator=model_creator,
                   optimizer_creator=optimizer_creator,
                   loss_creator=loss_creator
                   )

    @classmethod
    def from_tfkeras(cls, model_creator):
        return cls(backend="keras",
                   model_creator=model_creator)

    @classmethod
    def from_name(cls, name, dev_option="pytorch"):
        def get_class(base_class, class_name=name):
            mapping = {c.__name__: c for c in base_class.__subclasses__()}
            if class_name not in mapping.keys():
                raise ValueError(f"We don't have built-in {class_name} yet. "
                                 f"Please choose from {mapping.keys}")
            return mapping[class_name]

        if dev_option == 'pytorch':
            from zoo.automl.model.base_pytorch_model import PytorchBaseModel
            return cls(cls=get_class(PytorchBaseModel))

        elif dev_option == 'tf.keras':
            from zoo.automl.model.base_keras_model import KerasBaseModel
            return cls(cls=get_class(KerasBaseModel))

    @classmethod
    def from_cls(cls, estimator):
        return cls(cls=estimator)

    def build_from_ckpt(self, checkpoint_filename):
        '''Restore from a saved model'''
        if self.backend == "pytorch":
            from zoo.automl.model.base_pytorch_model import PytorchBaseModel
            model = PytorchBaseModel(**self.params)
            model.restore(checkpoint_filename)
            return model

        elif self.backend == "keras":
            from zoo.automl.model.base_keras_model import KerasBaseModel
            model = KerasBaseModel(**self.params)
            model.restore(checkpoint_filename)
            return model

    def build(self, config):
        '''Build a new model'''
        if self.backend == "pytorch":
            from zoo.automl.model.base_pytorch_model import PytorchBaseModel
            model = PytorchBaseModel(**self.params)
            model.build(config)
            return model

        elif self.backend == "keras":
            from zoo.automl.model.base_keras_model import KerasBaseModel
            model = KerasBaseModel(**self.params)
            model.build(config)
            return model

        elif self.cls is not None:
            return self.cls(config=config)

        else:
            builder = self.from_name(config["model"], dev_option=config["dev_option"])
            return builder.cls(config=config)
