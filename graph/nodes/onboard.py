import json
import subprocess
from graph.state import State

def onboard(state: State):
    print("---ONBOARDING DATA---")

    for args in state["data"]:
      result = subprocess.run(
        ['node', 'aden_tools.js', json.dumps(args)],
        capture_output=True,
        text=True
      )
      print("Node.js output:\n", result.stdout)
      print("Node.js errors:\n", result.stderr)
    
    return {}