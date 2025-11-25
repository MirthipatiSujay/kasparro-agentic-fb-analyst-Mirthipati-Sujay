from src.orchestrator.run_impl import main
if __name__=='__main__':
    import sys
    q = ' '.join(sys.argv[1:]) if len(sys.argv)>1 else "Analyze ROAS drop"
    main(q)
