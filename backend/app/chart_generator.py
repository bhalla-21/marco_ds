import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import base64
from io import BytesIO
import logging

# Mondelez brand colors with additional palette for variety
MONDELEZ_PALETTE = ["#5F2C56", "#9A3D88", "#D75C9C", "#E884BE", "#78C4D4", "#4CAF50", "#FF9800", "#9C27B0"]
BENCHMARK_COLOR = "#666666"

def render_chart(chart_spec: dict) -> str:
    """
    Enhanced chart renderer with multiple chart types and compact layout
    """
    try:
        logging.info(f"Rendering chart with spec keys: {list(chart_spec.keys())}")
        
        # Set compact styling
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette(MONDELEZ_PALETTE)
        
        chart_type = chart_spec.get('chart_type', chart_spec.get('type', 'bar'))
        title = chart_spec.get('title', 'Chart')
        data_list = chart_spec.get('data', [])
        benchmark_data = chart_spec.get('benchmark_data', [])
        
        logging.info(f"Chart type: {chart_type}, Data items: {len(data_list)}")
        
        if not data_list:
            logging.warning("No data provided for chart")
            return None
            
        df = pd.DataFrame(data_list)
        logging.info(f"Chart DataFrame columns: {list(df.columns)}")
        
        # Compact figure size for stacked layout
        fig, ax = plt.subplots(figsize=(12, 7))
        
        if chart_type == 'combination':
            return _render_combination_chart(df, benchmark_data, title, fig, ax)
        elif chart_type == 'stacked_bar':
            return _render_stacked_bar_chart(df, benchmark_data, title, fig, ax)
        elif chart_type == 'line':
            return _render_line_chart(df, benchmark_data, title, fig, ax)
        elif chart_type == 'pie':
            return _render_pie_chart(df, title, fig, ax)
        elif chart_type == 'scatter':
            return _render_scatter_chart(df, benchmark_data, title, fig, ax)
        elif chart_type == 'box':
            return _render_box_chart(df, title, fig, ax)
        elif chart_type == 'waterfall':
            return _render_waterfall_chart(df, title, fig, ax)
        else:
            return _render_bar_chart(df, benchmark_data, title, fig, ax)
            
    except Exception as e:
        logging.error(f"Error rendering chart: {e}", exc_info=True)
        return None

def _render_combination_chart(df, benchmark_data, title, fig, ax):
    """Dual-axis combination chart"""
    try:
        if 'Revenue' in df.columns and 'Volume' in df.columns:
            # Revenue bars
            bars = ax.bar(df['label'], df['Revenue'], alpha=0.8, color=MONDELEZ_PALETTE[0], label='Revenue')
            ax.set_ylabel('Revenue (M)', color=MONDELEZ_PALETTE[0])
            
            # Volume line on secondary axis  
            ax2 = ax.twinx()
            line = ax2.plot(df['label'], df['Volume'], color=MONDELEZ_PALETTE[1], 
                           marker='o', linewidth=3, markersize=8, label='Volume')
            ax2.set_ylabel('Volume (MM Kgs)', color=MONDELEZ_PALETTE[1])
            
            # Add benchmark if provided
            if benchmark_data:
                bench_df = pd.DataFrame(benchmark_data)
                ax.bar(bench_df['label'], bench_df.get('Revenue', 0), 
                      alpha=0.5, color=BENCHMARK_COLOR, label='Benchmark Revenue')
        
        elif 'Act' in df.columns:
            # Handle Act, rf, py columns
            bars = ax.bar(df['label'], df['Act'], alpha=0.8, color=MONDELEZ_PALETTE[0], label='Actual')
            if 'rf' in df.columns:
                ax.bar(df['label'], df['rf'], alpha=0.6, color=MONDELEZ_PALETTE[1], label='Reforecast')
            if 'py' in df.columns:
                ax.plot(df['label'], df['py'], color=MONDELEZ_PALETTE[2], 
                       marker='s', linewidth=3, markersize=8, label='Prior Year')
            ax.legend()
    
        _finalize_chart(fig, ax, title)
        return _save_chart(fig)
    except Exception as e:
        logging.error(f"Error in combination chart: {e}")
        return None

def _render_stacked_bar_chart(df, benchmark_data, title, fig, ax):
    """Stacked bar chart for category analysis"""
    try:
        # Get numeric columns (exclude 'label')
        numeric_cols = [col for col in df.columns if col != 'label' and pd.api.types.is_numeric_dtype(df[col])]
        
        if not numeric_cols:
            logging.warning("No numeric columns found for stacked bar chart")
            return _render_bar_chart(df, benchmark_data, title, fig, ax)
        
        bottom = np.zeros(len(df))
        for i, col in enumerate(numeric_cols):
            ax.bar(df['label'], df[col], bottom=bottom, 
                   color=MONDELEZ_PALETTE[i % len(MONDELEZ_PALETTE)], 
                   label=col, alpha=0.8)
            bottom += df[col]
        
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        _finalize_chart(fig, ax, title)
        return _save_chart(fig)
    except Exception as e:
        logging.error(f"Error in stacked bar chart: {e}")
        return None

def _render_line_chart(df, benchmark_data, title, fig, ax):
    """Line chart for trend analysis"""
    try:
        if 'value' in df.columns:
            ax.plot(df['label'], df['value'], marker='o', linewidth=3, 
                    markersize=8, color=MONDELEZ_PALETTE[0], label='Actual')
        elif 'Act' in df.columns:
            ax.plot(df['label'], df['Act'], marker='o', linewidth=3, 
                    markersize=8, color=MONDELEZ_PALETTE[0], label='Actual')
            if 'rf' in df.columns:
                ax.plot(df['label'], df['rf'], marker='s', linewidth=2, 
                        linestyle='--', color=MONDELEZ_PALETTE[1], label='Reforecast')
            if 'py' in df.columns:
                ax.plot(df['label'], df['py'], marker='^', linewidth=2, 
                        linestyle=':', color=MONDELEZ_PALETTE[2], label='Prior Year')
            ax.legend()
        
        # Add benchmark line
        if benchmark_data:
            bench_df = pd.DataFrame(benchmark_data)
            ax.plot(bench_df['label'], bench_df['value'], marker='s', 
                    linewidth=2, linestyle='--', color=BENCHMARK_COLOR, 
                    label='Benchmark', alpha=0.7)
            ax.legend()
        
        _finalize_chart(fig, ax, title)
        return _save_chart(fig)
    except Exception as e:
        logging.error(f"Error in line chart: {e}")
        return None

def _render_pie_chart(df, title, fig, ax):
    """Pie chart for composition analysis"""
    try:
        if 'value' in df.columns and 'label' in df.columns:
            # Filter out zero or negative values
            df_filtered = df[df['value'] > 0]
            if df_filtered.empty:
                logging.warning("No positive values for pie chart")
                return None
                
            wedges, texts, autotexts = ax.pie(df_filtered['value'], labels=df_filtered['label'], 
                                             autopct='%1.1f%%', startangle=90,
                                             colors=MONDELEZ_PALETTE[:len(df_filtered)])
            
            # Enhance text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        return _save_chart(fig)
    except Exception as e:
        logging.error(f"Error in pie chart: {e}")
        return None

def _render_scatter_chart(df, benchmark_data, title, fig, ax):
    """Scatter plot for correlation analysis"""
    try:
        if 'x' in df.columns and 'y' in df.columns:
            scatter = ax.scatter(df['x'], df['y'], s=100, alpha=0.7, 
                               color=MONDELEZ_PALETTE[0], edgecolors='white', linewidth=2)
            
            # Add labels if available
            if 'label' in df.columns:
                for i, txt in enumerate(df['label']):
                    ax.annotate(txt, (df['x'].iloc[i], df['y'].iloc[i]), 
                               xytext=(5, 5), textcoords='offset points', fontsize=9)
            
            # Add trend line
            z = np.polyfit(df['x'], df['y'], 1)
            p = np.poly1d(z)
            ax.plot(df['x'], p(df['x']), "--", alpha=0.8, color=MONDELEZ_PALETTE[1])
        
        _finalize_chart(fig, ax, title)
        return _save_chart(fig)
    except Exception as e:
        logging.error(f"Error in scatter chart: {e}")
        return None

def _render_box_chart(df, title, fig, ax):
    """Box plot for distribution analysis"""
    try:
        if 'category' in df.columns and 'values' in df.columns:
            # Prepare data for box plot
            box_data = []
            for values in df['values']:
                if isinstance(values, str):
                    try:
                        box_data.append(eval(values))
                    except:
                        box_data.append([float(values)])
                else:
                    box_data.append(values if isinstance(values, list) else [values])
            
            bp = ax.boxplot(box_data, labels=df['category'], patch_artist=True)
            
            # Color the boxes
            for patch, color in zip(bp['boxes'], MONDELEZ_PALETTE):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
        
        _finalize_chart(fig, ax, title)
        return _save_chart(fig)
    except Exception as e:
        logging.error(f"Error in box chart: {e}")
        return None

def _render_waterfall_chart(df, title, fig, ax):
    """Waterfall chart for P&L analysis"""
    try:
        if 'label' in df.columns and 'value' in df.columns:
            # Calculate cumulative values for waterfall effect
            cumulative = df['value'].cumsum()
            
            for i, (label, value) in enumerate(zip(df['label'], df['value'])):
                color = MONDELEZ_PALETTE[0] if value >= 0 else MONDELEZ_PALETTE[2]
                bottom = cumulative[i-1] if i > 0 else 0
                ax.bar(label, abs(value), bottom=bottom if value >= 0 else cumulative[i],
                      color=color, alpha=0.8)
                
                # Add value labels
                ax.text(i, cumulative[i] + (0.02 * max(cumulative)), 
                       f'{value:+.1f}', ha='center', va='bottom', fontweight='bold')
        
        _finalize_chart(fig, ax, title)
        return _save_chart(fig)
    except Exception as e:
        logging.error(f"Error in waterfall chart: {e}")
        return None

def _render_bar_chart(df, benchmark_data, title, fig, ax):
    """Standard bar chart"""
    try:
        if 'value' in df.columns:
            bars = ax.bar(df['label'], df['value'], color=MONDELEZ_PALETTE[0], alpha=0.8)
        elif 'Act' in df.columns:
            bars = ax.bar(df['label'], df['Act'], color=MONDELEZ_PALETTE[0], alpha=0.8, label='Actual')
            if 'rf' in df.columns:
                ax.bar(df['label'], df['rf'], color=MONDELEZ_PALETTE[1], alpha=0.6, label='Reforecast')
            if 'py' in df.columns:
                ax.bar(df['label'], df['py'], color=MONDELEZ_PALETTE[2], alpha=0.6, label='Prior Year')
            ax.legend()
        else:
            # Fallback: use first numeric column
            numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
            if numeric_cols:
                bars = ax.bar(df['label'], df[numeric_cols[0]], color=MONDELEZ_PALETTE[0], alpha=0.8)
        
        # Add benchmark bars if provided
        if benchmark_data:
            bench_df = pd.DataFrame(benchmark_data)
            ax.bar(bench_df['label'], bench_df['value'], 
                  color=BENCHMARK_COLOR, alpha=0.5, label='Benchmark')
            ax.legend()
        
        _finalize_chart(fig, ax, title)
        return _save_chart(fig)
    except Exception as e:
        logging.error(f"Error in bar chart: {e}")
        return None

def _finalize_chart(fig, ax, title):
    """Apply consistent styling to all charts"""
    try:
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        # Remove top and right spines for cleaner look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
    except Exception as e:
        logging.error(f"Error finalizing chart: {e}")

def _save_chart(fig):
    """Save chart to base64 string"""
    try:
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', 
                    facecolor='white', edgecolor='none')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        logging.error(f"Error saving chart: {e}")
        plt.close(fig)
        return None
