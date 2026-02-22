from beangulp import Ingest

from spiir import spiir

if __name__ == "__main__":
    ingest = Ingest([spiir.SpiirImporter()])
    ingest()
