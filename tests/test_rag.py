"""Run:  python -m unittest discover tests"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.loader import load_chunks
from rag.retriever import Retriever

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class TestRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = Retriever(load_chunks(DATA))

    def top(self, q):
        return self.r.search(q, k=1)[0][0].source

    def test_salt(self):
        self.assertEqual(self.top("Why is seawater salty?"), "01_ocean_basics.txt")

    def test_tides(self):
        self.assertEqual(self.top("What causes tides?"), "04_tides_and_waves.txt")

    def test_coral(self):
        self.assertEqual(self.top("What is coral bleaching?"), "06_coral_reefs.txt")

    def test_acid(self):
        self.assertEqual(self.top("What is ocean acidification?"), "07_climate_and_acidification.txt")

    def test_offtopic_low_score(self):
        hits = self.r.search("Who won the cricket world cup?", k=1)
        self.assertTrue(not hits or hits[0][1] < 0.085)


if __name__ == "__main__":
    unittest.main()
