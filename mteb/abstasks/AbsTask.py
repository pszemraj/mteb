from __future__ import annotations

import random
from abc import ABC, abstractmethod

import datasets
import numpy as np
import torch


class AbsTask(ABC):
    def __init__(self, seed=42, **kwargs):
        self.dataset = None
        self.data_loaded = False
        self.is_multilingual = False
        self.is_crosslingual = False
        self.save_suffix = kwargs.get("save_suffix", "")

        self.seed = seed
        random.seed(self.seed)
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        torch.cuda.manual_seed_all(self.seed)

    def load_data(self, **kwargs):
        """
        Load dataset from HuggingFace hub
        """
        if self.data_loaded:
            return

        # TODO: add split argument
        download_config = datasets.DownloadConfig(max_retries=5)
        self.dataset = datasets.load_dataset(
            self.metadata_dict["hf_hub_name"],
            revision=self.metadata_dict.get("revision", None),
            download_config=download_config,
        )
        self.data_loaded = True

    @property
    @abstractmethod
    def metadata_dict(self) -> dict[str, str]:
        """
        Returns a description of the task. Should contain the following fields:
        name: Name of the task (usually equal to the class name. Should be a valid name for a path on disc)
        description: Longer description & references for the task
        type: Of the set: [sts]
        eval_splits: Splits used for evaluation as list, e.g. ['dev', 'test']
        main_score: Main score value for task
        """
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, model, split="test"):
        """
        Evaluates a Sentence Embedding Model on the task.
        Returns a dict (that can be serialized to json).
        :param model: Sentence embedding method. Implements a encode(sentences) method, that encodes sentences
        and returns a numpy matrix with the sentence embeddings
        :param split: Which datasplit to be used.
        """
        raise NotImplementedError
