# app/chart_generator.py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import base64
from io import BytesIO

# Define a Mondelēz-inspired color palette (approximated from brand colors)
# Deep Purple, Bright Purple, Pink, Light Pink, etc.
MONDELEZ_PALETTE = ["#5F2C56", "#9A3D88", "#D75C9C", "#E884BE", "#78C4D4", "#4CAF50"]


def render_chart(chart_spec: dict) -> str:
    """
    Renders a compact, branded chart using Seaborn and returns it as a
    base64 encoded string.
    """
    try:
        # Set the custom Mondelēz color palette as the default
        sns.set_theme(style="whitegrid", palette=MONDELEZ_PALETTE)

        title = chart_spec.get('title', 'Chart')
        data_list = chart_spec.get('data', [])

        if not data_list:
            return None

        df = pd.DataFrame(data_list)

        # --- Dual-axis combo chart ---
        if 'Revenue' in df.columns and 'Volume' in df.columns and 'label' in df.columns:
            df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce').fillna(0)
            df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0)

            # Use a smaller figure size for a compact layout
            fig, ax1 = plt.subplots(figsize=(8, 5))

            # Revenue Bar Chart (Primary Axis)
            sns.barplot(x='label', y='Revenue', data=df, ax=ax1, alpha=0.8, label='Revenue')
            ax1.set_ylabel('Revenue', fontsize=12)
            ax1.set_xlabel(None)

            # Volume Line Chart (Secondary Axis)
            ax2 = ax1.twinx()
            sns.lineplot(
                x='label',
                y='Volume',
                data=df,
                marker='o',
                sort=False,
                color=MONDELEZ_PALETTE[3],
                ax=ax2,
                label='Volume'
            )
            ax2.set_ylabel('Volume', fontsize=12)

            fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)

        # --- Single-metric charts ---
        else:
            df['value'] = pd.to_numeric(df.get('value', 0), errors='coerce').fillna(0)
            chart_type = chart_spec.get('chart_type', 'bar')

            plt.figure(figsize=(8, 5))  # Compact figure
            if chart_type == 'bar':
                sns.barplot(x='label', y='value', data=df)
            elif chart_type == 'line':
                sns.lineplot(x='label', y='value', data=df, marker='o', sort=False)
            elif chart_type == 'pie':
                plt.pie(df['value'], labels=df['label'], autopct='%1.1f%%', startangle=140)

        plt.title(title, fontsize=16, weight='bold', pad=15)
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout(rect=[0, 0, 0.95, 1])  # Adjust layout for legend

        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=96)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{img_base64}"

    except Exception as e:
        print(f"Error rendering themed chart: {e}")
        return None





