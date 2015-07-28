%This class require the fucntion ini2struct from:
%http://www.mathworks.com/matlabcentral/fileexchange/17177-ini2struct


classdef iibm_loader
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
        function obj = iibm_loader(FileName)
           obj.reg_filename = FileName;
           obj.struct_config = ini2struct(strcat(FileName,'-0'));
           obj.fs= str2double(obj.struct_config.general.fs);
           obj.adc_scale =  str2double(obj.struct_config.general.adc_scale);
           obj.data_channels =  str2double(obj.struct_config.general.channels);
           obj.nfiles =  str2double(obj.struct_config.data_info.files);
           obj.samples4file =  str2double(obj.struct_config.data_info.samples4file);
           obj.samples4lastfile =  str2double(obj.struct_config.data_info.samples4lastfile);
           obj.total_samples = obj.samples4file * (obj.nfiles - 1) + obj.samples4lastfile;
           
           
           obj.data_channels = obj.data_channels+1; %plus 1 non-electrode channel
        end
        
        function data = get_data(obj, channels, beg_time, final_time)
        %
		% Usage:
		%       channels is a vector from 1 to the data_channels,
		% with the selected channels

            switch nargin
                 case 1
                     channels = 'all';
                     beg_time = 0;
                     final_time= 'end';
                 case 2
                     beg_time = 0;
                     final_time= 'end';
                 case 3
                     final_time= 'end';
            end
            beg_sample = floor(beg_time* obj.fs);
            if obj.total_samples < beg_sample
				error('beg_time out of data.')
            end
            beg_file = floor(beg_sample/obj.samples4file);
            rel_beg_sample = beg_sample - beg_file * obj.samples4file +1;
            if strcmp(channels,'all')
               channels = [1:obj.data_channels];
            end
            if strcmp(final_time,'end')
               final_sample = obj.total_samples;
            else
                final_sample = ceil(final_time* obj.fs);
            end 
            if final_sample <= beg_sample
				error('final < beginning.')
            end
            final_file = floor(final_sample/obj.samples4file);
            rel_final_sample = final_sample - final_file * obj.samples4file +1;
            data = zeros(size(channels,2),final_sample-beg_sample);
            if beg_file ~= final_file
            %inicio:
                fid = fopen(strcat(obj.reg_filename,'-',num2str(beg_file+1)),'r'); %plus 1, because data began in 1
                data_aux = fread(fid,[obj.data_channels,obj.samples4file],'int16');
                data(:, 1:obj.samples4file - rel_beg_sample) = data_aux(channels,rel_beg_sample:end);
                writed_samples = obj.samples4file - rel_beg_sample+1; %begins in the first element dont writed
                fclose(fid);

                %final
                fid = fopen(strcat(obj.reg_filename, '-', num2str(final_file + 1)), 'r'); %plus 1, because data began in 1
                data_aux = fread(fid, [obj.data_channels,obj.samples4file], 'int16');
                data(:, end - rel_final_sample:end) = data_aux(channels,1:rel_final_sample);
                fclose(fid);
		
                for i = [beg_file+1,final_file+1]
                    fid = fopen(strcat(obj.reg_filename, '-', num2str(i + 1)), 'r'); %plus 1, because data began in 1
                    data_aux = fread(fid,[obj.data_channels,obj.samples4file],'int16');
                    data(:, writed_samples:writed_samples+obj.samples4file) = data_aux(channels,:);
                    

                    writed_samples = writed_samples+obj.samples4file+1; %begins in the first element dont writed
                    fclose(fid);
                end
				
            else

                fid = fopen(strcat(obj.reg_filename, '-', num2str(beg_file + 1)), 'r'); %plus 1, because data began in 1
                data_aux = fread(fid,[obj.data_channels,obj.samples4file],'int16');
                data = data_aux(channels,rel_beg_sample:rel_final_sample);          
            
            end

        end
        
    end
end


