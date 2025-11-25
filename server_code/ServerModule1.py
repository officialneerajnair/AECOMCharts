import anvil.server
import pandas as pd
import io

@anvil.server.callable
def process_excel_file(file):
  # 1. Load Data
  file_bytes = file.get_bytes()
  df = pd.read_excel(io.BytesIO(file_bytes))

  # 2. Pre-processing
  date_col = df.columns[0]
  df[date_col] = pd.to_datetime(df[date_col])
  df = df.sort_values(by=date_col) # Sort by date once

  # Convert dates to string format for JSON/Plotly transfer
  x_values = df[date_col].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()

  # 3. Identify DMAs
  # We scan columns to find unique DMA prefixes
  dma_map = {} # Structure: {'DMA_ID': [list of trace dicts]}

  for col in df.columns[1:]:
    if "_" in col:
      dma_name = col.split("_")[0]

      # Initialize list if new DMA
      if dma_name not in dma_map:
        dma_map[dma_name] = []

        # Determine Axis and Style
      is_pressure = False
      if col.endswith("P") or col.endswith("AZP") or col.endswith("CP"):
        is_pressure = True
      elif "Q" in col:
        is_pressure = False
      else:
        continue # Skip unknown column types

        # Create the Trace Object
      trace = {
        'x': x_values,
        'y': df[col].fillna(0).tolist(),
        'name': col,
        'mode': 'lines',
        'type': 'scatter',
        'meta': dma_name # Tag the trace for reference
      }

      if is_pressure:
        trace['yaxis'] = 'y1'
        trace['line'] = {'width': 2}
      else:
        trace['yaxis'] = 'y2'
        trace['line'] = {'dash': 'dot', 'width': 2}

      dma_map[dma_name].append(trace)

  return dma_map