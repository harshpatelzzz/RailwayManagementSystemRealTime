/**
 * Main JavaScript for RailSewa Dashboard
 */

let currentFilter = 'all';
let responseModal;

$(document).ready(function() {
    // Initialize Bootstrap modal
    responseModal = new bootstrap.Modal(document.getElementById('responseModal'));
    
    // Character counter for response textarea
    $('#response-text').on('input', function() {
        const length = $(this).val().length;
        $('#char-count').text(length);
        
        if (length > 280) {
            $('#char-count').css('color', '#dc3545');
        } else {
            $('#char-count').css('color', '#6c757d');
        }
    });
    
    // Load initial data
    loadStats();
    loadTweets();
    
    // Auto-refresh every 30 seconds
    setInterval(function() {
        loadStats();
        loadTweets();
    }, 30000);
});

function loadStats() {
    $.ajax({
        url: 'index.php',
        method: 'POST',
        data: {
            action: 'get_stats'
        },
        dataType: 'json',
        success: function(data) {
            $('#stat-total').text(data.total || 0);
            $('#stat-emergency').text(data.emergency || 0);
            $('#stat-feedback').text(data.feedback || 0);
            $('#stat-responded').text(data.responded || 0);
        },
        error: function(xhr, status, error) {
            console.error('Error loading stats:', error);
        }
    });
}

function loadTweets() {
    $.ajax({
        url: 'index.php',
        method: 'POST',
        data: {
            action: 'get_tweets',
            filter: currentFilter
        },
        dataType: 'json',
        success: function(data) {
            displayTweets(data);
        },
        error: function(xhr, status, error) {
            console.error('Error loading tweets:', error);
            $('#tweets-tbody').html('<tr><td colspan="8" class="text-center text-danger">Error loading tweets</td></tr>');
        }
    });
}

function displayTweets(tweets) {
    const tbody = $('#tweets-tbody');
    
    if (tweets.length === 0) {
        tbody.html('<tr><td colspan="8" class="text-center">No tweets found</td></tr>');
        return;
    }
    
    let html = '';
    
    tweets.forEach(function(tweet) {
        const typeBadge = tweet.prediction == 1 
            ? '<span class="badge-emergency">Emergency</span>'
            : '<span class="badge-feedback">Feedback</span>';
        
        const statusBadge = tweet.response_status == 1
            ? '<span class="badge-responded">Responded</span>'
            : '<span class="badge-pending">Pending</span>';
        
        const pnr = tweet.pnr ? tweet.pnr : '-';
        const time = new Date(tweet.time).toLocaleString();
        
        html += `
            <tr>
                <td>${tweet.id}</td>
                <td class="tweet-text">${escapeHtml(tweet.tweet)}</td>
                <td>${escapeHtml(tweet.username || 'Unknown')}</td>
                <td>${pnr}</td>
                <td>${typeBadge}</td>
                <td>${time}</td>
                <td>${statusBadge}</td>
                <td>
                    ${tweet.response_status == 0 
                        ? `<button class="btn btn-sm btn-primary btn-action" onclick="openResponseModal(${tweet.id}, '${escapeHtml(tweet.tweet)}')">
                            <i class="fas fa-reply"></i> Respond
                           </button>`
                        : `<span class="text-muted">${escapeHtml(tweet.response || 'No response')}</span>`
                    }
                </td>
            </tr>
        `;
    });
    
    tbody.html(html);
}

function filterTweets(filter) {
    currentFilter = filter;
    
    // Update button states
    $('.btn-group button').removeClass('active');
    
    if (filter === 'all') {
        $('.btn-group button:first').addClass('active');
    } else if (filter === 'emergency') {
        $('.btn-group button:nth-child(2)').addClass('active');
    } else if (filter === 'feedback') {
        $('.btn-group button:last').addClass('active');
    }
    
    loadTweets();
}

function openResponseModal(tweetId, tweetText) {
    $('#modal-tweet-id').val(tweetId);
    $('#modal-tweet-text').text(tweetText);
    $('#response-text').val('');
    $('#char-count').text('0');
    responseModal.show();
}

function submitResponse() {
    const tweetId = $('#modal-tweet-id').val();
    const response = $('#response-text').val();
    
    if (!response.trim()) {
        alert('Please enter a response');
        return;
    }
    
    if (response.length > 280) {
        alert('Response cannot exceed 280 characters');
        return;
    }
    
    $.ajax({
        url: 'index.php',
        method: 'POST',
        data: {
            action: 'respond_tweet',
            tweet_id: tweetId,
            response: response
        },
        dataType: 'json',
        success: function(data) {
            if (data.status === 'success') {
                responseModal.hide();
                loadTweets();
                loadStats();
                alert('Response sent successfully!');
            } else {
                alert('Error: ' + data.message);
            }
        },
        error: function(xhr, status, error) {
            alert('Error sending response: ' + error);
        }
    });
}

function refreshData() {
    loadStats();
    loadTweets();
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text ? text.replace(/[&<>"']/g, m => map[m]) : '';
}

