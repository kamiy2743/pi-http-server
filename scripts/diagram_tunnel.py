from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.network import Nginx
from diagrams.saas.cdn import Cloudflare
from diagrams.onprem.compute import Server
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_BASE = ROOT_DIR / "public" / "diagram-tunnel"

with Diagram(
    "",
    filename=str(OUTPUT_BASE),
    outformat="png",
    show=False,
    direction="LR",
    graph_attr={
        "rankdir": "LR",
        "pad": "0.35",
        "nodesep": "0.7",
        "ranksep": "0.9",
        "fontname": "Noto Sans CJK JP",
    },
    node_attr={
        "fontsize": "12",
        "fontname": "Noto Sans CJK JP",
    },
    edge_attr={
        "fontsize": "11",
        "fontname": "Noto Sans CJK JP",
        "color": "#4b5563",
    },
):
    visitor = Users("訪問者")
    cf = Cloudflare("Cloudflare")

    with Cluster(
        "Raspberry Pi",
        graph_attr={
            "style": "rounded,filled",
            "color": "#9ecae1",
            "bgcolor": "#e6f4ff",
            "fontname": "Noto Sans CJK JP",
            "margin": "20",
        },
    ):
        tunnel = Server("cloudflared\n（Tunnelクライアント）")
        nginx = Nginx("Nginx")

    visitor >> cf
    cf >> Edge(style="invis", minlen="2") >> tunnel
    tunnel >> Edge(label="接続\n（リクエストを受け取る）", minlen="2") >> cf
    tunnel >> nginx
