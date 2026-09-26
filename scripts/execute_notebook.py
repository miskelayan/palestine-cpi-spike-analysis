"""Execute the committed notebook from a clean kernel using this Python environment."""
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

def main():
    root = Path(__file__).resolve().parents[1]
    path = root / "notebooks/01_cpi_spike_analysis.ipynb"
    notebook = nbformat.read(path, as_version=4)
    manager = KernelManager(kernel_name="python3")
    manager.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    client = NotebookClient(notebook, timeout=300, kernel_manager=manager,
                            resources={"metadata": {"path": str(root)}})
    client.execute()
    # Remove execution timing metadata: retain counts and real outputs.
    for cell in notebook.cells:
        cell.metadata.pop("execution", None)
    nbformat.write(notebook, path)
    print(f"Executed {path.name} successfully")

if __name__ == "__main__":
    main()
