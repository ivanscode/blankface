files = dir('/home/ivan/face-frontilization/Images/results_temp/*.obj');
length = size(files);
w = waitbar(0, 'Processing...', 'Name', 'Converting to jpeg', 'CreateCancelBtn', 'setappdata(gcbf,''canceling'',1)');
fprintf('Size is %d\n', length(1));
count = 0;
parfor i = 1:length(1)
    %Do the thing
    
    obj = readObj(strcat('/home/ivan/face-frontilization/Images/results_temp/', files(i).name));
    f = genImg(obj);
    [folder, baseFileName, extension] = fileparts(files(i).name);
    saveas(f, strcat('output/', baseFileName), 'jpg');
    close(f);
    
end
close(w)
