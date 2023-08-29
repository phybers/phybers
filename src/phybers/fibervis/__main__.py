from .FiberVis import main, process_args, parser


if __name__ == "__main__":
    ns, args = parser.parse_known_args()
    if ns.help:
        parser.print_help()
    else:
        main(**process_args(ns))
