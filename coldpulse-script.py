import argparse
from coldpulse.inputs import prepare_darray
from coldpulse.outputs import get_output, save_output

def parse_args(arg_list=None):
    parser = argparse.ArgumentParser(description="Run the coldpulse script analysis on a given directory")

    # Required arguments
    parser.add_argument('--input_dir', type=str, required=True,
                        help='Directory of the input data')
    parser.add_argument('--output_dir', type=str, default=None,
                        help='Directory of the output results')
    parser.add_argument('--climatology_dir', type=str, default=None,
                        help='Directory of where the climatology data is stored')
    
    return parser.parse_args(arg_list)


def main(input_dir, output_dir, climatology_dir):
    data_in = prepare_darray(input_dir)
    df_output, ds_output, df_output_sub = get_output(data_in, climatology_dir)
    file_name = input_dir.split('/')[-1]
    save_output(df_output, 
            df_output_sub,
            ds_output,
            file_name,
            dir_name=output_dir)


if __name__=='__main__':
    args = parse_args()
    if args.input_dir.endswith('/'):
        args.input_dir =args.input_dir[:-1]
    if args.output_dir is None:
       args.output_dir = args.input_dir + '/_TSI_out'
    if args.climatology_dir is None:
       args.climatology_dir = args.input_dir + '/_climato'
    main(args.input_dir, args.output_dir, args.climatology_dir)