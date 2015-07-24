%This class require the fucntion ini2struct from:
%http://www.mathworks.com/matlabcentral/fileexchange/17177-ini2struct


classdef iibm_loader()
    properties
    reg_filename
    fs
    adc_scale
    data_channels
    nfiles
    samples4file
    samples4lastfile
    total_samples
    struct_config
    end
    methods
        function iibm = iibm_loader(FileName)
           reg_filename = FileName;
           struct_config = ini2struct(strcat(FileName,'-0'));
           fs= str2num(struct_config.general.f)s;
           adc_scale =  str2num(struct_config.general.adc_scale);
           data_channels =  str2num(struct_config.general.channels);
           nfiles =  str2num(struct_config.data_info.nfiles);
           samples4file =  str2num(struct_config.data_info.samples4file);
           samples4lastfile =  str2num(struct_config.data_info.samples4lastfile);
           total_samples = samples4file * (nfiles - 1) + samples4lastfile;
           
        end
        
        function data = get_data(channels,beg_time, final_time)
            switch nargin
                 case 0
                     channels = 'all';
                     beg_time = 0;
                     final_time= 'all';
                 case 1
                      beg_time = 0;
                     final_time= 'all';
                 case 2
                     final_time= 'all';
            end
            if strcmp(channels,'all')
               channels = [1:data_channels];
            if strcmp(final_time,'all')
               final_time = total_samples;    
            
            final_file = floor(final_sample/samples4file)
            rel_final_sample = final_sample - final_file * self.samples4file
            data = np.ndarray([len(channels),final_sample-beg_sample])
           
           
           %first block
            fid=fopen([reg_filename '_' num2str(n)],'r');
            data=fread(fid,[25,samples4file],'int16');
            canal=[canal data(4*(tetrodo_nro-1)+canal_nro,:)];
            strobe=[strobe data(25,:)];
            fclose(fid);
        end
        
    end
end





fname='240112';					%%%% Nombre de la sesion
for tetrodo_nro=1				%%%% la info esta agrupada por tetrodos y canales, cada tetrodo tiene 4 canales
    for canal_nro=2				%%%% si sequiere extraen el canal 10 por ejemplo, tetrodo_nro=3 y canal_nro=9
        canal=[];
        strobe=[];
        file_tot=213;				%%%% Poner aca la cantidad de archivos (no incluir el header)
        file_qty=10;				%%%% dejar este numero fijo al menos que haya muuuucha memoria
        file_length=801000;			%%%% longitud de cada archivo en bytes

        canal_filt_sm=[];ini=[];fin=[];
        L(1)=0;
        for k=1:file_qty:file_tot
            k
            canal=[];strobe=[];
            for n=k:min(file_tot,k+file_qty-1)
                fid=fopen([reg_filename '_' num2str(n)],'r');
                data=fread(fid,[25,samples4file],'int16');
                canal=[canal data(4*(tetrodo_nro-1)+canal_nro,:)];
                strobe=[strobe data(25,:)];
                fclose(fid);
            end
        end

    end
end
