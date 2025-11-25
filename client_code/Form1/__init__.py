from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import plotly.graph_objects as go

class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.master_data = {} # Stores the full dataset in browser memory

  def file_loader_1_change(self, file, **event_args):
    """Called when file is uploaded"""
    if file:
      Notification("Processing File... Please wait.", timeout=None).show()

      # 1. Get ALL data at once (Dictionary: {'DMA': [traces]})
      self.master_data = anvil.server.call('process_excel_file', file)

      # 2. Create Checkboxes
      self.create_dma_checkboxes()

      # 3. Setup the blank plot layout
      self.update_plot([]) 

      Notification("Data Ready! Select DMAs below.").show()

  def create_dma_checkboxes(self):
    """Generates a checkbox for each DMA found in the file"""
    self.dma_checkbox_panel.clear() # Clear old boxes

    # Sort keys alphabetically
    sorted_dmas = sorted(self.master_data.keys())

    for dma in sorted_dmas:
      # Create a new CheckBox component
      c = CheckBox(text=dma, checked=False)

      # Bind the 'change' event to our update function
      c.set_event_handler('change', self.on_checkbox_change)

      # Add to the visual panel
      self.dma_checkbox_panel.add_component(c)

  def on_checkbox_change(self, **event_args):
    """Runs instantly in the browser when any box is checked"""
    combined_traces = []

    # 1. Loop through all checkboxes in the panel
    for comp in self.dma_checkbox_panel.get_components():
      if isinstance(comp, CheckBox) and comp.checked:
        dma_name = comp.text
        # 2. Grab the pre-loaded data from memory
        traces = self.master_data.get(dma_name, [])
        combined_traces.extend(traces)

    # 3. Update plot
    self.update_plot(combined_traces)

  def update_plot(self, traces):
    # If no traces, set a blank list
    if not traces:
      self.plot_1.data = []
      return

    # Define Layout
    layout = {
      'title': {
        'text': 'Total Head Graph',
        'font': {'size': 24, 'family': 'Arial', 'color': '#333'}
      },
      'hovermode': 'x unified',
      'xaxis': {
        'title': 'Date & Time',
        'type': 'date',
        'tickformat': '%d/%m %H:%M',
        'automargin': True
      },
      'yaxis': {
        'title': 'Total Head',
        'titlefont': {'color': '#1f77b4'},
        'tickfont': {'color': '#1f77b4'},
        'showgrid': True
      },
      'yaxis2': {
        'title': 'Flow Rate',
        'titlefont': {'color': '#ff7f0e'},
        'tickfont': {'color': '#ff7f0e'},
        'overlaying': 'y', 
        'side': 'right',
        'showgrid': False
      },
      'legend': {'x': 1.1, 'y': 1},
      'height': 600,
      'margin': {'l': 60, 'r': 80, 't': 80, 'b': 60}
    }

    self.plot_1.data = traces
    self.plot_1.layout = layout