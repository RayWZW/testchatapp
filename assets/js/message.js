const videoEmbed = embedYouTubeVideo(formattedMessage);


function formatLinks(message) {
    const urlPattern = /(?<!\S)(https?:\/\/[^\s]+)/g;
    
    return message.replace(urlPattern, function(url) {
        const embedFunctions = [
            embedYouTubeVideo,
            embedYouTubeShorts,
            embedDiscordInvite,
            embedVimeo
        ];
    
        for (let embedFunction of embedFunctions) {
            const embed = embedFunction(url);
            if (embed) {
                return embed; // Return the first embed that matches
            }
        }
    
        // If no embeds were matched, return the original URL wrapped in an anchor tag
        return `<a href="${url}" class="link" target="_blank" rel="noopener noreferrer">${url}</a>`;
    });
    }

    