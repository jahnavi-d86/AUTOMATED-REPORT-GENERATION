!pip install fpdf

from google.colab import files
uploaded = files.upload()

import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

filename = list(uploaded.keys())[0]
df = pd.read_csv(filename)

time_col = None
for col in df.columns:
    if 'time' in col.lower() or 'date' in col.lower():
        try:
            df[col] = pd.to_datetime(df[col],format="%d.%m.%Y-%H:%M", errors='coerce')
            time_col = col
            break
        except:
            continue

if not time_col:
    time_col = df.columns[0]
    df[time_col] = pd.to_datetime(df[time_col])
numeric_cols = df.select_dtypes(include='number').columns.tolist()
output_col = next((col for col in numeric_cols if 'power' in col.lower() or 'output' in col.lower()), numeric_cols[0])

plt.figure(figsize=(10, 3))
plt.plot(df[time_col], df[output_col], color='orange', marker='o', linestyle='-')
plt.title("Solar Power Output Over Time")
plt.xlabel("Time")
plt.ylabel("Power Generation")
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(True)
plot_filename = "solar_output_chart.png"
plt.savefig(plot_filename)
plt.close()

summary = df.describe()
threshold = summary[output_col]['mean'] + summary[output_col]['std']
high_output_df = df[df[output_col] > threshold]
top5_df = df.sort_values(by=output_col, ascending=False).head(5)

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

pdf.cell(200, 10, txt="Solar Power Plant Data Report", ln=True, align="C")
pdf.ln(10)

pdf.set_font("Arial", 'B', 12)
pdf.cell(200, 10, txt=f"Summary for: {output_col}", ln=True)
pdf.set_font("Arial", size=11)
for stat in summary.index:
    value = round(summary[output_col][stat], 2)
    pdf.cell(200, 10, txt=f"{stat}: {value}", ln=True)
pdf.ln(5)

pdf.set_font("Arial", 'B', 12)
pdf.cell(200, 10, txt="Insights:", ln=True)
pdf.set_font("Arial", size=11)
pdf.cell(200, 10, txt=f"Threshold for high generation: {round(threshold, 2)}", ln=True)
pdf.cell(200, 10, txt=f"High output records: {len(high_output_df)}", ln=True)
pdf.ln(5)

pdf.set_font("Arial", 'B', 12)
pdf.cell(200, 10, txt="Top 5 Power Outputs:", ln=True)
pdf.set_font("Arial", size=11)
for _, row in top5_df.iterrows():
    time_str = row[time_col] if isinstance(row[time_col], str) else row[time_col].strftime("%Y-%m-%d %H:%M")
    pdf.cell(200, 10, txt=f"{time_str}: {row[output_col]:.2f}", ln=True)
pdf.ln(10)

pdf.image(plot_filename, x=10, y=pdf.get_y(), w=190)

pdf_file = "solar_power_report.pdf"
pdf.output(pdf_file)

files.download(pdf_file)
