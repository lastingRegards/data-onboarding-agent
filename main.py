from graph.graph import app
from test_vars import URL
import pprint




########################################################################################

# MAIN APP CALL
result = (app.invoke(input={"service":URL}))
for key in result:
    print("==================================================")
    print(key)
    pprint.pp(result[key])
