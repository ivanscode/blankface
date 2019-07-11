clear
clc
imgs=textread('lfw160.txt','%s');

cnt=11;

nrof_big_img=floor(length(imgs)/(cnt^2));

ind=1;
for i=1:nrof_big_img
    big_img=imread(['lfw_160_merged/m' int2str(i) '.jpg']);
    for j=1:cnt
        for k=1:cnt
            x=(j-1)*160+1:j*160;
            y=(k-1)*160+1:k*160;
            I=big_img(x,y,:);
            imwrite(I,['lfw_160_splitted/' imgs{ind}]);
            ind=ind+1;
        end
    end
    i
end

kCnt=11;
jCnt=ceil((length(imgs)-nrof_big_img*(cnt^2))/kCnt);
big_img=imread(['lfw_160_merged/m' int2str(i+1) '.jpg']);
for j=1:jCnt
    for k=1:kCnt
        x=(j-1)*160+1:j*160;
        y=(k-1)*160+1:k*160;
        I=big_img(x,y,:);
            imwrite(I,['lfw_160_splitted/' imgs{ind}]);
        ind=ind+1;
        if ind>length(imgs)
            break
        end
    end
    if ind>length(imgs)
        break
    end
end