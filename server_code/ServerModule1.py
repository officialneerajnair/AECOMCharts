import anvil.server
import anvil.media
import pandas as pd
import io
from anvil.tables import app_tables

@anvil.server.callable
def load_excel_file(file):
  # 1. CLEAR previous files (so we don't fill up the database)
  app_tables.temp_file_store.delete_all_rows()

  # 2. SAVE the new file to the database
  app_tables.temp_file_store.add_row(the_file=file)

  # 3. Process the file to get DMAs
  # Convert Anvil media to bytes for Pandas
  file_bytes = file.get_bytes()
  df = pd.read_excel(io.BytesIO(file_bytes))

  # Identify unique DMAs
  dma_set = set()
  for col in df.columns[1:]:
    if "_" in col:
      dma_part = col.split("_")[0]
      dma_set.add(dma_part)

  return sorted(list(dma_set))

@anvil.server.callable
def get_plot_data(selected_dma):
  # 1. RETRIEVE the file from the database
  row = app_tables.temp_file_store.search()[0] # Get the first (and only) row

  if not row:
    return None

    # 2. Load into Pandas
  file_bytes = row['the_file'].get_bytes()
  df = pd.read_excel(io.BytesIO(file_bytes))

  # Ensure Date is datetime (Assuming first column is Date)
  date_col = df.columns[0]
  df[date_col] = pd.to_datetime(df[date_col])

  # 3. Prepare data for Plotly
  traces = []
  x_values = df[date_col].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()

  # Find relevant columns
  relevant_cols = [c for c in df.columns if str(c).startswith(selected_dma + "_")]

  for col in relevant_cols:
    is_pressure = False
    if col.endswith("P") or col.endswith("AZP") or col.endswith("CP"):
      is_pressure = True

    trace = {
      'x': x_values,
      'y': df[col].fillna(0).tolist(),
      'name': col,
      'mode': 'lines',
      'type': 'scatter'
    }

    if is_pressure:
      trace['yaxis'] = 'y1'
      trace['line'] = {'width': 2}
    else:
      trace['yaxis'] = 'y2'
      trace['line'] = {'dash': 'dot', 'width': 2}

    traces.append(trace)

  return traces