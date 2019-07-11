clear
clc
imgs=textread('lfw160.txt','%s');

cnt=11;

nrof_big_img=floor(length(imgs)/(cnt^2));

ind=1;
for i=1:nrof_big_img
    big_img=zeros(cnt*160,cnt*160,3,'uint8');
    for j=1:cnt
        for k=1:cnt
            x=(j-1)*160+1:j*160;
            y=(k-1)*160+1:k*160;
            big_img(x,y,:)=imread(['lfw_2d/' imgs{ind}]);
            ind=ind+1;
        end
    end
    imwrite(big_img,['lfw_2d_merged/m' int2str(i) '.jpg']);
end

kCnt=11;
jCnt=ceil((length(imgs)-nrof_big_img*(cnt^2))/kCnt);
big_img=zeros(jCnt*160,kCnt*160,3,'uint8');
for j=1:jCnt
    for k=1:kCnt
        x=(j-1)*160+1:j*160;
        y=(k-1)*160+1:k*160;
        big_img(x,y,:)=imread(['lfw_2d/' imgs{ind}]);
        ind=ind+1;
        if ind>length(imgs)
            break
        end
    end
    if ind>length(imgs)
        break
    end
end
imwrite(big_img,['lfw_2d_merged/m' int2str(i+1) '.jpg']);