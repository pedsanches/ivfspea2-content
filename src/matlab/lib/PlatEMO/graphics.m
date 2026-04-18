figure;
boxplot([cell2mat(results(:,2)), cell2mat(results(:,4))], {'IGD', 'HV'});
title('Boxplot das Métricas');
ylabel('Valor da Métrica');
grid on;
