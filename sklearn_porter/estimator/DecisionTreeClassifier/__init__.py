from copy import deepcopy
from json import dumps, encoder
from textwrap import indent
from typing import Callable, Tuple, Union

from jinja2 import Environment
from loguru import logger as L

# scikit-learn
from sklearn.tree import \
    DecisionTreeClassifier as DecisionTreeClassifierClass

# sklearn-porter
from sklearn_porter import enums as enum
from sklearn_porter import exceptions as exception
from sklearn_porter.estimator.EstimatorApiABC import EstimatorApiABC
from sklearn_porter.estimator.EstimatorBase import EstimatorBase


class DecisionTreeClassifier(EstimatorBase, EstimatorApiABC):
    """Extract model data and port a DecisionTreeClassifier classifier."""

    SKLEARN_URL = 'sklearn.tree.DecisionTreeClassifier.html'

    DEFAULT_LANGUAGE = enum.Language.JAVA
    DEFAULT_TEMPLATE = enum.Template.ATTACHED
    DEFAULT_METHOD = enum.Method.PREDICT

    SUPPORT = {
        enum.Language.C: {
            enum.Template.ATTACHED: enum.ALL_METHODS,
            enum.Template.COMBINED: enum.ALL_METHODS,
        },
        enum.Language.GO: {
            enum.Template.ATTACHED: enum.ALL_METHODS,
            enum.Template.COMBINED: enum.ALL_METHODS,
            enum.Template.EXPORTED: enum.ALL_METHODS,
        },
        enum.Language.JAVA: {
            enum.Template.ATTACHED: enum.ALL_METHODS,
            enum.Template.COMBINED: enum.ALL_METHODS,
            enum.Template.EXPORTED: enum.ALL_METHODS,
        },
        enum.Language.JS: {
            enum.Template.ATTACHED: enum.ALL_METHODS,
            enum.Template.COMBINED: enum.ALL_METHODS,
            enum.Template.EXPORTED: enum.ALL_METHODS,
        },
        enum.Language.PHP: {
            enum.Template.ATTACHED: enum.ALL_METHODS,
            enum.Template.COMBINED: enum.ALL_METHODS,
            enum.Template.EXPORTED: enum.ALL_METHODS,
        },
        enum.Language.RUBY: {
            enum.Template.ATTACHED: enum.ALL_METHODS,
            enum.Template.COMBINED: enum.ALL_METHODS,
            enum.Template.EXPORTED: enum.ALL_METHODS,
        },
    }

    estimator = None  # type: DecisionTreeClassifierClass

    def __init__(self, estimator: DecisionTreeClassifierClass):
        super().__init__(estimator)
        L.info('Create specific estimator `%s`.', self.estimator_name)
        est = self.estimator  # alias

        # Is the estimator fitted?
        try:
            getattr(est, 'n_features_in_')  # for sklearn >  0.19
            getattr(est.tree_, 'value')  # for sklearn <= 0.18
        except AttributeError:
            raise exception.NotFittedEstimatorError(self.estimator_name)

        # Extract and save meta information:
        self.meta_info = dict(
            n_features=est.n_features_in_,
            n_classes=len(est.tree_.value.tolist()[0][0]),
        )
        L.info('Meta info (keys): {}'.format(self.meta_info.keys()))
        L.opt(lazy=True).debug('Meta info: {}'.format(self.meta_info))

        # Extract and save model data:
        self.model_data = dict(
            lefts=est.tree_.children_left.tolist(),
            rights=est.tree_.children_right.tolist(),
            thresholds=est.tree_.threshold.tolist(),
            indices=est.tree_.feature.tolist(),
            classes=[[int(c) for c in l[0]] for l in est.tree_.value.tolist()],
        )
        L.info('Model data (keys): {}'.format(self.model_data.keys()))
        L.opt(lazy=True).debug('Model data: {}'.format(self.model_data))

    def port(
        self,
        language: enum.Language,
        template: enum.Template,
        class_name: str,
        converter: Callable[[object], str],
        to_json: bool = False,
    ) -> Union[str, Tuple[str, str]]:
        """
        Port an estimator.

        Parameters
        ----------
        language : Language
            The required language.
        template : Template
            The required template.
        class_name : str
            Change the default class name which will be used in the generated
            output. By default the class name of the passed estimator will be
            used, e.g. `DecisionTreeClassifier`.
        converter : Callable
            Change the default converter of all floating numbers from the model
            data. By default a simple string cast `str(value)` will be used.
        to_json : bool (default: False)
            Return the result as JSON string.

        Returns
        -------
        out_class : str
            The ported estimator.
        """
        # Placeholders:
        plas = deepcopy(self.placeholders)  # alias
        plas.update(dict(
            class_name=class_name,
            to_json=to_json,
        ))
        plas.update(self.meta_info)

        # Templates:
        tpls = self._load_templates(language.value.KEY)

        # Make 'exported' variant:
        if template == enum.Template.EXPORTED:
            tpl_class = tpls.get_template('exported.class')
            out_class = tpl_class.render(**plas)
            # converter = kwargs.get('converter')
            encoder.FLOAT_REPR = lambda o: converter(o)
            model_data = dumps(self.model_data, separators=(',', ':'))
            return out_class, model_data

        # Make 'atatched' or 'combined' variant:
        # Pick templates:
        tpl_int = tpls.get_template('int').render()
        tpl_double = tpls.get_template('double').render()
        tpl_arr_1 = tpls.get_template('arr[]')
        tpl_arr_2 = tpls.get_template('arr[][]')
        tpl_in_brackets = tpls.get_template('in_brackets')

        # Make contents:
        lefts_val = list(map(str, self.model_data.get('lefts')))
        lefts_str = tpl_arr_1.render(
            type=tpl_int,
            name='lefts',
            values=', '.join(lefts_val),
            n=len(lefts_val),
        )

        rights_val = list(map(str, self.model_data.get('rights')))
        rights_str = tpl_arr_1.render(
            type=tpl_int,
            name='rights',
            values=', '.join(rights_val),
            n=len(rights_val),
        )

        thresholds_val = list(map(converter, self.model_data.get('thresholds')))
        thresholds_str = tpl_arr_1.render(
            type=tpl_double,
            name='thresholds',
            values=', '.join(thresholds_val),
            n=len(thresholds_val),
        )

        indices_val = list(map(str, self.model_data.get('indices')))
        indices_str = tpl_arr_1.render(
            type=tpl_int,
            name='indices',
            values=', '.join(indices_val),
            n=len(indices_val),
        )

        classes_val = [
            list(map(str, e)) for e in self.model_data.get('classes')
        ]
        classes_str = [', '.join(e) for e in classes_val]
        classes_str = ', '.join(
            [tpl_in_brackets.render(value=e) for e in classes_str]
        )
        classes_str = tpl_arr_2.render(
            type=tpl_int,
            name='classes',
            values=classes_str,
            n=len(classes_val),
            m=len(classes_val[0]),
        )

        plas.update(
            dict(
                lefts=lefts_str,
                rights=rights_str,
                thresholds=thresholds_str,
                indices=indices_str,
                classes=classes_str,
            )
        )

        # Make 'attached' variant:
        if template == enum.Template.ATTACHED:
            tpl_class = tpls.get_template('attached.class')
            out_class = tpl_class.render(**plas)
            return out_class

        # Make 'combined' variant:
        if template == enum.Template.COMBINED:
            tpl_class = tpls.get_template('combined.class')
            out_tree = self._create_tree(tpls, language, converter)
            plas.update(dict(tree=out_tree))
            out_class = tpl_class.render(**plas)
            return out_class

    def _create_tree(
        self,
        tpls: Environment,
        language: enum.Language,
        converter: Callable[[object], str],
    ):
        """
        Build a decision tree.

        Parameters
        ----------
        tpls : Environment
            All relevant templates.
        language : str
            The required language.
        converter : Callable[[object], str]
            The number converter.

        Returns
        -------
        A tree of a DecisionTreeClassifier.
        """
        n_indents = (
            1 if language in {
                enum.Language.JAVA, enum.Language.JS, enum.Language.PHP,
                enum.Language.RUBY
            } else 0
        )
        return self._create_branch(
            tpls,
            language,
            converter,
            self.model_data.get('lefts'),
            self.model_data.get('rights'),
            self.model_data.get('thresholds'),
            self.model_data.get('classes'),
            self.model_data.get('indices'),
            0,
            n_indents,
        )

    def _create_branch(
        self,
        tpls: Environment,
        language: enum.Language,
        converter: Callable[[object], str],
        left_nodes: list,
        right_nodes: list,
        threshold: list,
        value: list,
        features: list,
        node: int,
        depth: int,
    ):
        """
        The ported single tree as function or method.

        Parameters
        ----------
        tpls : Environment
            All relevant templates.
        language
            The required language.
        converter
            The number converter.
        left_nodes : list
            The left children node.
        right_nodes : list
            The left children node.
        threshold : list
            The decision thresholds.
        value : list
            The label or class.
        features : list
            The feature values.
        node : list
            The current node.
        depth : list
            The tree depth.

        Returns
        -------
        A single branch of a DecisionTreeClassifier.
        """
        out = ''
        out_indent = tpls.get_template('indent').render()
        if threshold[node] != -2.0:
            out += '\n'
            val_a = 'features[{}]'.format(features[node])
            if language is enum.Language.PHP:
                val_a = '$' + val_a
            val_b = converter(threshold[node])
            tpl_if = tpls.get_template('if')
            out_if = tpl_if.render(a=val_a, op='<=', b=val_b)
            out_if = indent(out_if, depth * out_indent)
            out += out_if

            if left_nodes[node] != -1.0:
                out += self._create_branch(
                    tpls,
                    language,
                    converter,
                    left_nodes,
                    right_nodes,
                    threshold,
                    value,
                    features,
                    left_nodes[node],
                    depth + 1,
                )

            out += '\n'
            out_else = tpls.get_template('else').render()
            out_else = indent(out_else, depth * out_indent)
            out += out_else

            if right_nodes[node] != -1.0:
                out += self._create_branch(
                    tpls,
                    language,
                    converter,
                    left_nodes,
                    right_nodes,
                    threshold,
                    value,
                    features,
                    right_nodes[node],
                    depth + 1,
                )

            out += '\n'
            out_endif = tpls.get_template('endif').render()
            out_endif = indent(out_endif, depth * out_indent)
            out += out_endif
        else:
            clazzes = []
            tpl = 'classes[{0}] = {1}'
            if language is enum.Language.PHP:
                tpl = '$' + tpl
            tpl = indent(tpl, depth * out_indent)

            for i, rate in enumerate(value[node]):
                if int(rate) > 0:
                    clazz = tpl.format(i, rate)
                    clazz = '\n' + clazz
                    clazzes.append(clazz)

            out_join = tpls.get_template('join').render()
            out += out_join.join(clazzes) + out_join
        return out
