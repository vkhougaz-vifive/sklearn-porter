# -*- coding: utf-8 -*-

from typing import Union, Optional, Callable
from logging import Logger, ERROR

from sklearn.neural_network.multilayer_perceptron import MLPClassifier \
    as MLPClassifierClass

from sklearn_porter.EstimatorApiABC import EstimatorApiABC
from sklearn_porter.estimator.EstimatorBase import EstimatorBase
from sklearn_porter.utils import get_logger


class MLPClassifier(EstimatorBase, EstimatorApiABC):
    """
    Extract model data and port a MLPClassifier classifier.

    See also
    --------
    http://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html
    """
    estimator = None  # type: MLPClassifierClass

    def __init__(
            self,
            estimator: MLPClassifierClass,
            logger: Union[Logger, int] = ERROR
    ):
        super().__init__(estimator)
        self.L = get_logger(__name__, logger=logger)
        self.L.info('Create specific estimator `%s`.', self.estimator_name)
        est = self.estimator  # alias

        # TODO: Export and prepare model data from estimator.

    def port(
            self,
            method: str = 'predict',
            to: Union[str] = 'java',  # language
            with_num_format: Callable[[object], str] = lambda x: str(x),
            with_class_name: Optional[str] = None,
            with_method_name: Optional[str] = None
    ) -> str:
        temps = self.load_templates(language=to)

        print(temps.keys())

        return str(self.estimator)