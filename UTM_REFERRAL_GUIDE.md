# Advanced UTM Referral Traffic Feature

## Overview

The Advanced UTM Referral Traffic feature allows you to generate and use UTM-tracked URLs for simulating referral traffic from 19+ social media platforms. This is ideal for testing analytics, campaign tracking, and understanding traffic sources.

## Features

### 🌐 19+ Social Media Platform Support

The following social media platforms are now supported:

1. **Facebook** - via Facebook link manager
2. **Google** - via Google redirect URL
3. **Twitter (X)** - via t.co shortener
4. **Telegram** - via Telegram share
5. **Instagram** - via Instagram link redirect
6. **Reddit** - via Reddit outbound tracker
7. **LinkedIn** - via LinkedIn redirect
8. **Pinterest** - via Pinterest sharing
9. **YouTube** - via YouTube redirect
10. **TikTok** - via TikTok redirect
11. **WhatsApp** - via WhatsApp share
12. **Snapchat** - via Snapchat add
13. **Discord** - via Discord invite
14. **Medium** - via Medium redirect
15. **Quora** - via Quora share
16. **Tumblr** - via Tumblr share
17. **VK** - via VK share
18. **Weibo** - via Weibo share
19. **LINE** - via LINE share

### 📊 UTM Parameter Support

The feature supports all standard UTM parameters:

- **utm_source**: Automatically set based on selected platform (e.g., 'facebook', 'twitter')
- **utm_medium**: Selectable from dropdown (social, paid_social, influencer, referral, cpc, display)
- **utm_campaign**: User-defined campaign name (e.g., 'summer_sale_2024')
- **utm_term**: Optional targeting keywords
- **utm_content**: Optional content identifier (e.g., 'banner_ad_1')

### 🎯 Multi-Platform Selection

- Select single or multiple platforms
- Traffic is randomly distributed across selected platforms
- Each visit uses a randomly selected platform from your choices
- Realistic referral patterns with proper referer headers

## How to Use

### Step 1: Select Referral Traffic Mode

1. Open the ADVANCED-BOT application
2. Navigate to the **Website Configuration** tab
3. Under **Visit Type**, select **"Referral Visit"**

### Step 2: Configure UTM Parameters

In the **Advanced UTM Referral Traffic Generator** section:

1. **Campaign Name**: Enter your campaign identifier (e.g., `summer_sale_2024`)
   - This field is optional but recommended
   - If left empty, basic referral traffic will be used without UTM parameters

2. **UTM Medium**: Select from the dropdown:
   - `social` - Organic social traffic
   - `paid_social` - Paid social campaigns
   - `influencer` - Influencer marketing
   - `referral` - General referral traffic
   - `cpc` - Cost-per-click campaigns
   - `display` - Display advertising

3. **UTM Term** (Optional): Add targeting keywords
   - Example: `premium_users`, `tech_enthusiasts`

4. **UTM Content** (Optional): Specify content variant
   - Example: `banner_ad_1`, `video_campaign`, `post_123`

### Step 3: Select Social Platforms

In the **Select Social Media Platforms** section:

1. Check one or more platforms from the list
2. At least one platform must be selected
3. The bot will randomly select from your chosen platforms for each visit

### Step 4: Configure Traffic Settings

Continue with standard traffic settings:
- Number of tabs/visits
- Time to spend per profile
- Platform (Desktop/Android)
- Other behavior settings

### Step 5: Start Traffic Generation

Click **"Start Automation"** to begin generating referral traffic with UTM parameters.

## Example URLs Generated

### Basic Example
**Input:**
- Website: `https://example.com`
- Platform: Facebook
- Campaign: `summer_sale_2024`
- Medium: `social`

**Generated URL:**
```
https://example.com?utm_source=facebook&utm_medium=social&utm_campaign=summer_sale_2024
```

### Complete Example
**Input:**
- Website: `https://example.com/products`
- Platform: Instagram
- Campaign: `influencer_promo`
- Medium: `influencer`
- Term: `fashion_bloggers`
- Content: `story_link_1`

**Generated URL:**
```
https://example.com/products?utm_source=instagram&utm_medium=influencer&utm_campaign=influencer_promo&utm_term=fashion_bloggers&utm_content=story_link_1
```

## Traffic Flow

The bot follows this flow for referral traffic:

1. **Selects Random Platform**: Chooses one platform from your selected list
2. **Visits Referrer**: Opens the platform's referral URL (e.g., facebook.com, twitter.com)
3. **Simulates Human Behavior**: Scrolls and waits on referrer page
4. **Navigates to Target**: Opens your website with UTM parameters and proper referer header
5. **Continues Browsing**: Performs configured browsing behaviors on your site

## Use Cases

### Marketing Campaign Tracking
```
Campaign: holiday_sale_2024
Medium: paid_social
Platforms: Facebook, Instagram, TikTok
Term: gift_shoppers
Content: carousel_ad_1
```

### Influencer Marketing
```
Campaign: product_launch
Medium: influencer
Platforms: Instagram, YouTube, TikTok
Term: tech_reviewers
Content: sponsored_post
```

### Social Media Testing
```
Campaign: brand_awareness
Medium: social
Platforms: All 19 platforms
Content: organic_post
```

### A/B Testing
```
Test A:
- Campaign: test_campaign_v1
- Content: variant_a

Test B:
- Campaign: test_campaign_v1
- Content: variant_b
```

## Benefits

1. **Accurate Analytics Testing**: Test your Google Analytics or other analytics platforms with realistic UTM-tracked traffic

2. **Campaign Attribution**: Verify that your attribution models correctly identify traffic sources

3. **Multi-Platform Diversity**: Simulate traffic from 19+ different social platforms

4. **Realistic Referral Patterns**: Each platform uses its authentic referral URL pattern (e.g., Facebook uses lm.facebook.com, Twitter uses t.co)

5. **Flexible Configuration**: Mix and match platforms, campaigns, and content variations

## Technical Details

### UTM Parameter Handling

The bot automatically:
- Preserves existing query parameters in URLs
- Properly URL-encodes all parameters
- Sets appropriate referer headers
- Follows platform-specific referral patterns

### Platform-Specific Referral URLs

Each platform uses authentic referral patterns:
- **Facebook**: `https://lm.facebook.com/l.php`
- **Twitter**: `https://t.co`
- **Instagram**: `https://l.instagram.com`
- **And more...**

This ensures that traffic appears realistic and follows actual platform behaviors.

## Notes

- **Campaign Name**: While optional, it's recommended to always provide a campaign name for proper UTM tracking
- **Platform Selection**: Select multiple platforms for more diverse traffic patterns
- **Random Distribution**: Traffic is randomly distributed across selected platforms
- **Realistic Behavior**: The bot simulates human behavior including scrolling, waiting, and natural navigation

## Troubleshooting

### No UTM Parameters in URLs

**Issue**: URLs don't contain UTM parameters
**Solution**: Make sure you've entered a Campaign Name. If left empty, basic referral traffic is used without UTM parameters.

### Only One Platform Used

**Issue**: Traffic only comes from one platform despite selecting multiple
**Solution**: This is normal - each individual visit randomly selects one platform. Run multiple visits to see distribution across platforms.

### Analytics Not Showing Traffic

**Issue**: Google Analytics or other tools not showing the traffic
**Solution**: 
1. Verify UTM parameters are in the URL
2. Check your analytics filters aren't blocking the traffic
3. Ensure cookies are being set properly
4. Allow time for analytics to process (can take 24-48 hours)

## Version History

- **v1.0** (Current): Added advanced UTM referral traffic with 19 social platforms
- Initial support for all standard UTM parameters
- Multi-platform selection with random distribution
