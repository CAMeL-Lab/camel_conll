import plotly.graph_objects as go
import pandas as pd

if __name__ == '__main__':
    # Import plotly and create a figure
    fig = go.Figure()


    # Filter the dataframe so that it doesn't crash the browser with too much data
    # from mitosheet import filter_df_to_safe_size
    # df4_filtered, _ = filter_df_to_safe_size('scatter', df4, ['DEPREL_child', 'id_parent-id_child'])
    df = pd.read_csv('./data/patterns/pattern_list_full.tsv', sep='\t')
    df['id_parent-id_child'] = df['ID_parent'] - df['ID_child']
    
    # Add the scatter traces to the figure
    for column_header in ['UPOS_child', 'UPOS_parent']:
        fig.add_trace(go.Scatter(
            x=df[column_header],
            y=df['id_parent-id_child'],
            mode='markers',
            name=column_header
        ))

    # Update the layout
    # See Plotly documentation for cutomizations: https://plotly.com/python/reference/scatter/
    fig.update_layout(
        xaxis_title='DEPREL_child',
        yaxis_title='id_parent-id_child',
        title='DEPREL_child, id_parent-id_child scatter plot',
    )
    fig.show()
    # fig.show(renderer="iframe")