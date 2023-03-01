from dash import Dash, html, Input, Output
import dash_cytoscape as cyto

app = Dash(__name__)

import whatap_node_matrix7th as wnm
elements = wnm.getMatrix()

app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape-compound',
        zoom=100,
        zoomingEnabled=True,
        layout={"name": "preset", "fit":False, "zoom":0.5},
        #layout={"name": "circle", "fit":True, "zoom":1, "padding": 10},
        # layout={"name": "concentric", "fit":True, "zoom":1},
        #layout={"name": "breadthfirst"},
        # layout={"name": "cose",
        #     "refresh": 20, 
        #     "fit": True,
        #     # Node repulsion (non overlapping) multiplier
        #     # "nodeRepulsion":  1024,
        #     #Node repulsion (overlapping) multiplier
        #     # "nodeOverlap":8,
        #     "idealEdgeLength": 32,
        #     "edgeElasticity": 32,
        #     "randomize": False,
        #     "componentSpacing": 40,
        #     "nestingFactor": 1.2,
        #     "gravity": 1,
        #     "numIter": 1000,
        #     "initialTemp": 1000,
        #     "coolingFactor": 0.99,
        #     "minTemp": 1.0
        # },
        style={'width': '100%', 'height': '900px'},
        stylesheet=[
            {
                'selector': 'node',
                'style': {'content': 'data(label)'}
            },
            {
                'selector': '.edges',
                'style': {'width': 0.5,'target-arrow-shape': 'triangle','curve-style': 'bezier'}
            },
        ],
        elements=elements
    ),
    dcc.Markdown(id='cytoscape-selectedNodeData-markdown')
])

@app.callback(Output('cytoscape-selectedNodeData-markdown', 'children'),
              Input('cytoscape-compound', 'selectedNodeData'))
def displaySelectedNodeData(data_list):
    if data_list is None:
        return "No node selected."

    nodes_list = [data['label'] for data in data_list]
    return "You selected the following nodes: " + "\n* ".join(nodes_list)

if __name__ == '__main__':
    app.run_server(debug=True)
