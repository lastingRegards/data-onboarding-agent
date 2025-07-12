from graph.graph import app
from test_vars import URL




########################################################################################

# MAIN APP CALL
print(app.invoke(input={"service":URL})["service"])
