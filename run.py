from classification import Classification
from tqdm import tqdm
import os

##Automatically runs 12 experiments with different parameters


if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"]='0'
    with tqdm(initial=0,total=12) as pbar:
        #12 experiements varying:
            #model {bert, roberta, xlnet}
            #plot_type {wiki, tmdb}
            #frozen {true, false}
        for model in ['bert','roberta','xlnet']:
            for is_wiki in [True,False]:
                plot_type = 'wiki' if is_wiki else 'tmdb'
                max_length = 400 if is_wiki else 60
                #Reduce max_length for XLNet with Wiki to ensure it runs
                if model == 'xlnet' and is_wiki:
                    max_length = 300
                for freeze in [True,False]:
                    print(f'####### Running {model} with {plot_type}{" (frozen)" if freeze else ""} #######')
                    file_name = f'{model}_{plot_type}_results_{max_length}{"_freeze" if freeze else ""}.pkl'
                    classification = Classification(model,plot_type,file_name,True,freeze,max_length)
                    classification.run()
                    pbar.update(1)
        
