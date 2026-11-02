"""CutPost 脚本入口（由 AI 工具调用）：python <skill目录>/scripts/run.py <命令> …"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cutpost.__main__ import main
main()
