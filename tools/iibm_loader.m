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
        %
		% Usage:
		%       channels is a vector from 1 to the data_channels,
		% with the selected channels
        
            switch nargin
                 case 0
                     channels = 'all';
                     beg_time = 0;
                     final_time= 'end';
                 case 1
                     beg_time = 0;
                     final_time= 'end';
                 case 2
                     final_time= 'end';
            end
            
            if total_samples < beg_sample
				error('beg_time out of data.')
            end
            if strcmp(channels,'all')
               channels = [1:data_channels];
            end
            if strcmp(final_time,'end')
               final_time = total_samples;    
            end 
            if final_sample <= beg_sample
				error('final < beginning.')
			end
            final_file = floor(final_sample/samples4file);
            rel_final_sample = final_sample - final_file * samples4file;
            data = zeros(size(channels,2),final_sample-beg_sample)
            if beg_file != final_file
				%inicio:
				fid = fopen(strcat(reg_filename,"-",num2str(beg_file+1)),'r'); #plus 1, because data began in 1
				data(:, 1:samples4file - rel_beg_sample) = fread(fid,[data_channels,samples4file],'int16')(channels,rel_beg_sample:end);
				writed_samples = samples4file - rel_beg_sample;
				fclose(fid);
				
				#final
				fid = fopen(strcat(reg_filename, "-", num2str(final_file + 1)), 'r'); #plus 1, because data began in 1
				data(:, end - rel_final_sample:end) = fread(fid, [data_channels,samples4file], 'int16')(channels,1:rel_final_sample);
				fclose(fid);
				
				for i = [beg_file+1,final_file+1]
					fid = fopen(strcat(reg_filename, "-", num2str(i + 1)), 'r'); #plus 1, because data began in 1
					data(:, writed_samples:writed_samples+samples4file) = fread(fid,[data_channels,samples4file],'int16')(channels,:);
					fclose(fid);
				end
				
            else
				fid = fopen(strcat(reg_filename, "-", num2str(beg_file + 1)), 'r'); #plus 1, because data began in 1
                data = fread(fid,[data_channels,samples4file],'int16')(channels,rel_beg_sample:rel_final_sample);          
            
            end

        end
        
    end
end


