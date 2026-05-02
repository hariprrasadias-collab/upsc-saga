export const generateConfettiStyles = (count: number) => {
    return [...Array(count)].map(() => ({
        left: `${Math.random() * 100}%`,
        animationDelay: `${Math.random() * 0.5}s`,
        backgroundColor: ['#f1c40f', '#e74c3c', '#3498db', '#2ecc71', '#9b59b6'][Math.floor(Math.random() * 5)]
    }));
};
