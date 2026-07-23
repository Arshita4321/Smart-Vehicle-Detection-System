import streamlit as st

def render_charts(analytics_instance, trend_placeholder, conf_placeholder, dist_placeholder):
    trend_chart = analytics_instance.get_trend_chart()
    if trend_chart:
        trend_placeholder.plotly_chart(trend_chart, use_container_width=True, key=f"trend_chart")
        
    conf_chart = analytics_instance.get_confidence_chart()
    if conf_chart:
        conf_placeholder.plotly_chart(conf_chart, use_container_width=True, key=f"conf_chart")
        
    dist_chart = analytics_instance.get_class_distribution_chart()
    if dist_chart:
        dist_placeholder.plotly_chart(dist_chart, use_container_width=True, key=f"dist_chart")
