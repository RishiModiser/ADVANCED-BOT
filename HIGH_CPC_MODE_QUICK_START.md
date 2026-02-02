# HIGH CPC/CPM Mode - Quick Start Guide

## What is HIGH CPC/CPM Mode?

HIGH CPC/CPM Mode is an advanced feature that simulates high-value website traffic by:
1. Opening a High CPC website in 4 tabs with cookie handling and shopping interactions
2. Visiting your target domain with natural browsing behavior
3. Performing timed interactions (scrolling, clicking) on your target domain

## How to Use

### Step 1: Enable the Feature

1. Open the Advanced Bot application
2. Go to the **Traffic Settings** tab (first tab)
3. Scroll down to find the **💰 HIGH CPC/CPM Mode** section
4. Check the box **"✅ Enable HIGH CPC/CPM Mode"**

### Step 2: Configure URLs

Once enabled, you'll see three input fields:

1. **High CPC Website URL**
   - Enter the URL of a high-value website (e.g., an e-commerce site)
   - Example: `https://example-shop.com`
   - This site will be opened in 4 tabs

2. **Target Domain URL**
   - Enter your target website URL
   - Example: `https://your-website.com`
   - This is where you want to drive traffic

3. **Target Stay Time (seconds)**
   - Set how long to spend on your target domain
   - Default: 180 seconds (3 minutes)
   - Range: 30-3600 seconds
   - Recommended: 180-300 seconds for realistic behavior

### Step 3: Configure Other Settings

Don't forget to configure these important settings:

- **Concurrent**: Number of profiles to run simultaneously (start with 1-5 for testing)
- **Platform**: Select Windows and/or Android
- **Proxy Settings**: Configure proxies if needed (recommended for multiple profiles)

### Step 4: Start the Bot

1. Click the **▶ START** button
2. Watch the log output to see the process:
   - "HIGH CPC/CPM Mode enabled" message
   - Tab-by-tab progress updates
   - Shopping interaction status
   - Target domain interaction progress

### Step 5: Monitor Execution

The bot will log each step:

```
✓ HIGH CPC/CPM Mode enabled
  High CPC URL: https://example-shop.com...
  Target Domain: https://your-website.com...
  Target Stay Time: 180 seconds

━━━ Profile 1 | HIGH CPC/CPM Mode | Platform: windows ━━━
Creating browser context for HIGH CPC mode...
Opening High CPC URL in 4 tabs: https://example-shop.com...
Tab 1: Loading High CPC URL...
Tab 2: Loading High CPC URL...
Tab 3: Loading High CPC URL...
Tab 4: Loading High CPC URL...
All 4 tabs loaded, starting cookie handling...
Tab 1: Cookie popup accepted
Tab 2: No cookie popup found, moving on
Tab 3: Cookie popup accepted
Tab 4: Starting shopping interaction flow...
Tab 4: Clicked button: Add to Cart
Tab 4: Navigated to cart
Tab 4: Proceeded to checkout
Tab 4: Filling checkout form with random data...
Opening Target Domain in 5th tab: https://your-website.com...
Starting Target Domain interaction (stay time: 180 seconds)...
Performing 2 initial random clicks...
Waiting until half-time (90s)...
Half-time reached, performing 2 more clicks...
Stay time completed, closing all tabs...
✓ HIGH CPC/CPM Mode Profile 1 completed successfully
```

## Example Use Cases

### Use Case 1: E-commerce Traffic Simulation
```
High CPC URL: https://popular-store.com
Target Domain: https://your-store.com
Stay Time: 240 seconds
Concurrent: 3

Result: Simulates users browsing a popular store, then visiting your store
```

### Use Case 2: Content Site Traffic
```
High CPC URL: https://major-news-site.com
Target Domain: https://your-blog.com
Stay Time: 180 seconds
Concurrent: 5

Result: Simulates users reading news, then visiting your blog
```

### Use Case 3: Local Business
```
High CPC URL: https://directory-site.com
Target Domain: https://your-local-business.com
Stay Time: 150 seconds
Concurrent: 2

Result: Simulates users browsing directory, then visiting your business site
```

## Best Practices

### ✅ DO:
- Start with 1-5 concurrent profiles for testing
- Use reputable, legitimate websites for High CPC URL
- Set realistic stay times (180-300 seconds)
- Monitor logs during first few runs
- Use proxies for higher concurrency
- Test with single profile before scaling up

### ❌ DON'T:
- Use very short stay times (< 30 seconds)
- Run too many concurrent profiles without proxies
- Use suspicious or low-quality High CPC sites
- Set unrealistic stay times (> 600 seconds may look automated)
- Ignore error messages in logs

## Troubleshooting

### Issue: "No clickable elements found"
**Solution**: Normal behavior if Target Domain has limited interactive elements. The bot will continue with scrolling.

### Issue: "Shopping interaction error"
**Solution**: High CPC website structure may not match expected patterns. The bot will skip shopping flow and continue to Target Domain.

### Issue: "Cookie popup not found"
**Solution**: Normal behavior if website doesn't have cookie popups. The bot continues execution.

### Issue: Tabs not closing properly
**Solution**: Check log for error messages. Ensure sufficient system resources (RAM, CPU).

### Issue: Slow execution
**Solution**: 
- Reduce concurrent profiles
- Check internet connection speed
- Verify proxy performance if using proxies

## Advanced Configuration

### Combining with Other Features

HIGH CPC/CPM Mode works with:

- ✅ **Proxy Rotation**: Each profile uses a different proxy
- ✅ **Platform Selection**: Mix Windows and Android browsers
- ✅ **Concurrency**: Run multiple HIGH CPC profiles simultaneously
- ✅ **Cookie Import**: Use imported cookies for High CPC sites
- ✅ **User-Agent Rotation**: Different user agents per profile

### Performance Tuning

For optimal performance:

1. **Low Concurrency (1-5 profiles)**
   - Good for: Testing, low-resource systems
   - Proxy needed: Optional
   - RAM requirement: 2-4 GB

2. **Medium Concurrency (5-20 profiles)**
   - Good for: Regular usage, medium traffic goals
   - Proxy needed: Recommended
   - RAM requirement: 4-8 GB

3. **High Concurrency (20+ profiles)**
   - Good for: High traffic goals, professional use
   - Proxy needed: Required
   - RAM requirement: 8-16 GB+

## Safety Notes

⚠️ **Important Considerations**:

1. Always respect website Terms of Service
2. Use responsibly and ethically
3. Don't overload target websites
4. Use appropriate delays and stay times
5. Monitor for any issues or errors
6. Use proxies to avoid IP bans

## Support

If you encounter issues:

1. Check the logs for error messages
2. Review this guide for common solutions
3. Verify all URLs are correct and accessible
4. Test with single profile first
5. Check system resources (CPU, RAM, network)

## Summary

HIGH CPC/CPM Mode adds sophisticated traffic simulation capabilities:
- ✅ Multi-tab High CPC website interaction
- ✅ Automatic cookie handling (Tabs 1-4)
- ✅ Shopping flow simulation (Tab 4)
- ✅ Natural target domain browsing (Tab 5)
- ✅ Timed interactions with mid-time actions
- ✅ Human-like behavior patterns
- ✅ Full integration with existing features

Start with simple configurations and scale up as you become familiar with the feature!
