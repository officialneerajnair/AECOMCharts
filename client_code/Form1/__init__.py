from ._anvil_designer import Form1Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go

class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Disable dropdown until file is loaded
    self.dma_dropdown.enabled = False

  def file_loader_1_change(self, file, **event_args):
    """This method is called when a file is loaded"""
    if file:
      Notification("Processing Excel File...").show()

      # Call server to parse file and get DMA list
      dma_list = anvil.server.call('load_excel_file', file)

      # Populate dropdown
      self.dma_dropdown.items = dma_list
      self.dma_dropdown.enabled = True

      Notification("File Loaded! Select a DMA.").show()

  def dma_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    selected_dma = self.dma_dropdown.selected_value
    print(f"User selected: {selected_dma}") 

    if selected_dma:
      # Get trace data from server
      traces_data = anvil.server.call('get_plot_data', selected_dma)
      print(f"Server returned {len(traces_data) if traces_data else 'None'} traces")

      if traces_data:
        self.plot_chart(traces_data)
      else:
        Notification("No data found for this DMA").show()

  def plot_chart(self, traces):
    # Define Layout for Dual Axis
    layout = {
      'title': f'Pressure & Flow for {self.dma_dropdown.selected_value}',
      'xaxis': {'title': 'Date & Time'},

      # Left Y Axis (Pressure)
      'yaxis': {
        'title': 'Pressure',
        'titlefont': {'color': '#1f77b4'},
        'tickfont': {'color': '#1f77b4'}
      },

      # Right Y Axis (Flow)
      'yaxis2': {
        'title': 'Flow Rate',
        'titlefont': {'color': '#ff7f0e'},
        'tickfont': {'color': '#ff7f0e'},
        'overlaying': 'y', 
        'side': 'right'
      },
      'legend': {'x': 1.1, 'y': 1}, 
      'height': 600
    }

    # Render the plot
    self.plot_1.data = traces
    self.plot_1.layout = layout