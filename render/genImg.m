function fig = genImg(obj)
%
% function displayObj(obj)
%
% obj - wavefront file
%

tval=obj.v(:,3); 
fig = figure('visible', 'off'); 
patch('vertices',obj.v,'faces',obj.f.v, 'FaceVertexCData', tval);
shading flat;
colormap gray(256);
lighting phong;
camproj('perspective');
material dull;
camlight('headlight', 'infinite');
axis square; 
axis off;
axis equal
axis tight;
%cameramenu