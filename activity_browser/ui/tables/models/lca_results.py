# -*- coding: utf-8 -*-
import numpy as np

from .base import PandasModel


class LCAResultsModel(PandasModel):
    def sync(self, df):
        self._dataframe = df.replace(np.nan, '', regex=True)
        self.updated.emit()


class InventoryModel(PandasModel):
    def sync(self, df):
        self._dataframe = df
        # set the visible columns
        self.visible_columns = {col: i for i, col in enumerate(self._dataframe.columns.to_list())}
        # set the columns te be defined as num (all except the first five for both biopshere and technosphere
        self.different_column_types = {col: 'num' for i, col in enumerate(self._dataframe.columns.to_list()) if i >= 5}
        self.updated.emit()


class ContributionModel(PandasModel):
    def sync(self, df):
        self._dataframe = df.replace(np.nan, '', regex=True)
        self.updated.emit()
