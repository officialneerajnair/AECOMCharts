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
      # 1. CHART TITLE
      'title': {
        'text': 'Total Head Graph',
        'font': {'size': 24, 'family': 'Arial', 'color': '#333'}
      },

      # 2. UNIFIED TOOLTIP (Shows all values for the specific time)
      'hovermode': 'x unified',

      # 3. X-AXIS CONFIGURATION
      'xaxis': {
        'title': 'Date & Time',
        'type': 'date',
        'tickformat': '%d/%m %H:%M',
        'automargin': True
      },

      # 4. LEFT Y-AXIS (Pressure / Total Head)
      'yaxis': {
        'title': 'Total Head',
        'titlefont': {'color': '#1f77b4', 'size': 14},
        'tickfont': {'color': '#1f77b4'},
        'showgrid': True
      },

      # 5. RIGHT Y-AXIS (Flow Rate)
      'yaxis2': {
        'title': 'Flow Rate',
        'titlefont': {'color': '#ff7f0e', 'size': 14},
        'tickfont': {'color': '#ff7f0e'},
        'overlaying': 'y', 
        'side': 'right',
        'showgrid': False
      },

      # Legend and Margins
      'legend': {
        'x': 1.1, 
        'y': 1,
        'bgcolor': 'rgba(255,255,255,0.5)'
      },
      'height': 600,
      'margin': {'l': 60, 'r': 80, 't': 80, 'b': 60}
    }

    # Render the plot
    self.plot_1.data = traces
    self.plot_1.layout = layout