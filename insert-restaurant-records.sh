#!/bin/bash

# Script to insert synthetic restaurant records into DynamoDB
# This script creates 30 diverse restaurant records with realistic data

TABLE_NAME="Restaurants"
REGION="us-east-1"  # Change this to your AWS region if needed

# Function to insert a restaurant record
insert_restaurant() {
  local restaurant_id=$1
  local name=$2
  local cuisine=$3
  local city=$4
  local address=$5
  local lat=$6
  local lng=$7
  local description=$8
  local price_range=$9
  local rating=${10}
  local capacity=${11}

  aws dynamodb put-item \
    --table-name "$TABLE_NAME" \
    --region "$REGION" \
    --item "{
      \"restaurantId\": {\"S\": \"$restaurant_id\"},
      \"name\": {\"S\": \"$name\"},
      \"cuisine\": {\"S\": \"$cuisine\"},
      \"city\": {\"S\": \"$city\"},
      \"location\": {
        \"M\": {
          \"address\": {\"S\": \"$address\"},
          \"city\": {\"S\": \"$city\"},
          \"coordinates\": {
            \"M\": {
              \"lat\": {\"N\": \"$lat\"},
              \"lng\": {\"N\": \"$lng\"}
            }
          }
        }
      },
      \"description\": {\"S\": \"$description\"},
      \"priceRange\": {\"S\": \"$price_range\"},
      \"rating\": {\"N\": \"$rating\"},
      \"capacity\": {\"N\": \"$capacity\"},
      \"menuCard\": {
        \"L\": [
          {
            \"M\": {
              \"category\": {\"S\": \"Main Course\"},
              \"items\": {
                \"L\": [
                  {\"S\": \"Signature Dish 1\"},
                  {\"S\": \"Signature Dish 2\"},
                  {\"S\": \"Signature Dish 3\"}
                ]
              }
            }
          },
          {
            \"M\": {
              \"category\": {\"S\": \"Appetizers\"},
              \"items\": {
                \"L\": [
                  {\"S\": \"Appetizer 1\"},
                  {\"S\": \"Appetizer 2\"}
                ]
              }
            }
          }
        ]
      },
      \"openHours\": {
        \"M\": {
          \"monday\": {\"S\": \"11:00-23:00\"},
          \"tuesday\": {\"S\": \"11:00-23:00\"},
          \"wednesday\": {\"S\": \"11:00-23:00\"},
          \"thursday\": {\"S\": \"11:00-23:00\"},
          \"friday\": {\"S\": \"11:00-00:00\"},
          \"saturday\": {\"S\": \"12:00-00:00\"},
          \"sunday\": {\"S\": \"12:00-22:00\"}
        }
      },
      \"createdAt\": {\"S\": \"2024-01-15T10:30:00Z\"}
    }"
  
  echo "✓ Inserted: $name ($restaurant_id)"
}

# Insert Restaurant 1: Italian Bistro
insert_restaurant "rest_001" \
  "Italian Bistro" \
  "Italian" \
  "New York" \
  "123 Main St, Downtown" \
  "40.7128" \
  "-74.0060" \
  "Welcome to Italian Bistro, your gateway to authentic Italian culinary traditions in the heart of downtown Manhattan. Since opening our doors, we have been dedicated to bringing the true flavors of Italy to New York's discerning palates. Our kitchen is led by Chef Marco Giuliano, who trained under master chefs in Rome, Tuscany, and the Amalfi Coast. Every dish on our menu tells a story of Italian regional cuisine, from the rich seafood pastas of the Mediterranean to the hearty risottos of Piedmont. We source only the finest imported ingredients directly from Italy, including San Marzano tomatoes, Parmigiano-Reggiano, and authentic Italian wines. Our intimate setting features exposed brick walls, candlelit tables, and soft lighting. The wine list showcases over 150 Italian selections. Whether indulging in Pasta Carbonara or delicate Branzino al Forno, each meal celebrates Italian hospitality and culinary excellence." \
  "$$" \
  "4.5" \
  "50"

# Insert Restaurant 2: Tokyo Ramen House
insert_restaurant "rest_002" \
  "Tokyo Ramen House" \
  "Japanese" \
  "New York" \
  "456 Park Ave" \
  "40.7614" \
  "-73.9776" \
  "Experience the essence of Tokyo's street food culture at Tokyo Ramen House, where tradition meets excellence. Our master ramen chefs have spent decades perfecting their craft, from simmering the perfect broth for 18 hours to hand-pulling noodles with precision. Every bowl of ramen is a work of art, combining umami-rich tonkotsu broths, tender chashu pork, and perfectly soft-boiled eggs. Beyond our signature ramen, we serve authentic Japanese street food including crispy gyoza dumplings and yakitori skewers grilled over charcoal. Our intimate counter seating offers an authentic Tokyo izakaya experience, with our chefs visible through the kitchen window. The atmosphere buzzes with energy as locals and tourists gather to share bowls of warming ramen. We pride ourselves on using only premium Japanese ingredients imported directly from Tokyo, ensuring every flavor profile remains authentic. Whether you are a ramen connoisseur or discovering Japanese cuisine for the first time, Tokyo Ramen House promises an unforgettable culinary journey to the vibrant streets of Japan's capital city." \
  "$$$" \
  "4.7" \
  "45"

# Insert Restaurant 3: El Mariachi
insert_restaurant "rest_003" \
  "El Mariachi" \
  "Mexican" \
  "Los Angeles" \
  "789 Sunset Blvd" \
  "34.0897" \
  "-118.3200" \
  "El Mariachi brings the vibrant spirit and authentic flavors of Mexico to the heart of Los Angeles. Our restaurant celebrates the rich culinary heritage of Mexico, with recipes passed down through generations and techniques refined over centuries. From the moment you enter, you are enveloped in Mexican warmth—colorful papel picado decorations flutter overhead, and traditional mariachi music sets the festive mood. Our kitchen showcases regional Mexican cuisine with house-made moles containing 25+ ingredients, hand-pressed corn tortillas made fresh throughout the day, and ceviche prepared with the catch of the day. Each dish reflects our commitment to authenticity—from our Chile Relleno with Oaxacan cheese to our slow-roasted Carnitas and our signature Chiles en Nogada during special seasons. Our bar features over 100 premium tequilas and mezcals, expertly mixed into traditional margaritas and innovative cocktails. The open kitchen allows you to witness the artistry of our chefs as they work their magic. Whether celebrating with family or experiencing Mexican cuisine for the first time, El Mariachi offers an authentic, memorable journey through Mexico's diverse food traditions." \
  "$$" \
  "4.3" \
  "60"

# Insert Restaurant 4: The French Table
insert_restaurant "rest_004" \
  "The French Table" \
  "French" \
  "San Francisco" \
  "321 California St" \
  "37.7749" \
  "-122.4194" \
  "The French Table represents the pinnacle of French culinary sophistication in San Francisco, offering an exquisite dining experience that honors centuries of gastronomic tradition. Our elegant dining room features crystal chandeliers, soft candlelight, and pristine white tablecloths that define fine dining excellence. Executive Chef Laurent Beaumont, trained at Michelin-starred establishments in Lyon and Paris, curates a seasonally-inspired menu showcasing classical French techniques elevated with modern sensibilities. From delicate amuse-bouches to perfectly seared duck confit with cherry gastrique, each course is a masterpiece of flavor and presentation. Our sommelier has handpicked a wine collection featuring over 300 selections, predominantly French vintages from renowned regions including Bordeaux, Burgundy, and Alsace. We offer both à la carte dining and our chef's tasting menu, which takes guests on a culinary journey through France's regional specialties. Our commitment to quality extends to sourcing—we work with specialized purveyors to secure the finest ingredients, from Brittany lobster to Provençal truffles. Whether celebrating a milestone, enjoying a romantic dinner, or seeking world-class French cuisine, The French Table provides an unforgettable evening of elegance and culinary artistry." \
  "$$$" \
  "4.8" \
  "40"

# Insert Restaurant 5: Taj Mahal
insert_restaurant "rest_005" \
  "Taj Mahal" \
  "Indian" \
  "Chicago" \
  "654 Michigan Ave" \
  "41.8781" \
  "-87.6298" \
  "Taj Mahal represents the grandeur and sophistication of Indian cuisine in an elegantly appointed setting on Michigan Avenue. Named after one of the world's most magnificent structures, our restaurant mirrors that same attention to detail and beauty. Our culinary team, led by Master Chef Rajesh Kumar from Delhi, brings over 30 years of expertise in North Indian, South Indian, and regional Himalayan cuisines. Every spice blend is meticulously crafted in-house, and we grind fresh spices daily to ensure maximum flavor and authenticity. Our menu journeys through India's diverse regions—from creamy butter chicken and tender tandoori meats to the coconut-infused curries and dosas of the south. The tandoor produces perfectly charred breads and succulent proteins impossible to achieve through conventional methods. Our extensive list of craft cocktails blends Indian spices with premium spirits, while our wine selection features bottles that pair beautifully with complex curry flavors. The dining room showcases warm amber lighting, intricate tapestries, and traditional Indian artwork. Our attentive staff guides you through the menu, explaining regional variations. Whether a devoted curry enthusiast or discovering Indian cuisine's depths for the first time, Taj Mahal delivers an extraordinary culinary voyage through India's most celebrated flavors." \
  "$$" \
  "4.6" \
  "55"

# Insert Restaurant 6: Beijing Duck House
insert_restaurant "rest_006" \
  "Beijing Duck House" \
  "Chinese" \
  "San Francisco" \
  "987 Grant Ave" \
  "37.7969" \
  "-122.4071" \
  "Beijing Duck House stands as San Francisco's premier destination for authentic Peking duck and traditional Chinese cuisine, a legacy built over three decades of culinary excellence. Our signature Peking duck is prepared using a centuries-old technique passed down from Beijing's imperial kitchens. Each duck is meticulously air-dried, glazed with a secret malt syrup blend, and roasted in our custom-built ovens to achieve the perfect balance of crispy exterior and succulent meat. The presentation is theatrical—ducks arrive at your table whole, where our expert carvers demonstrate the artful tradition of separating meat, skin, and fat. Beyond our legendary duck, our menu showcases premium dim sum served from rolling carts, hand-pulled noodles prepared by expert noodle makers, and seafood specialties reflecting Cantonese culinary mastery. The Hong Kong-style dining room bustles with energy—family-style shared plates and round tables perfect for celebrations. Our sommelier curates selections that bridge East and West flavors. Whether enjoying a family gathering, celebrating special occasions, or embarking on a gastronomic journey through Chinese regional cuisines, Beijing Duck House delivers an authentic, memorable dining experience that honors tradition while welcoming all palates." \
  "$$$" \
  "4.4" \
  "65"

# Insert Restaurant 7: O Fado
insert_restaurant "rest_007" \
  "O Fado" \
  "Portuguese" \
  "Boston" \
  "111 Hanover St" \
  "42.3601" \
  "-71.0589" \
  "O Fado brings the soulful traditions of Portugal to Boston's historic North End, offering an authentic Portuguese dining experience steeped in warmth and hospitality. Named after Portugal's most iconic musical tradition, our restaurant embodies the same emotional depth and passion in every dish. Our chef trained in Lisbon, Porto, and the Algarve region, bringing deep knowledge of Portuguese regional cooking that extends far beyond what most diners expect. The seafood takes center stage—fresh catches from both Atlantic and Mediterranean traditions are prepared with simplicity that lets quality ingredients shine. Grilled sardines, perfectly seared scallops in garlic and white wine, hearty fish stews, and our signature Cataplana fish steamed in traditional Portuguese copper cookware showcase Portugal's maritime heritage. Beyond seafood, we offer traditional meat dishes like slow-braised octopus, tender rabbit in red wine, and succulent caldo verde—Portugal's beloved green soup. Our wine list celebrates Portuguese vintages from regions like Douro, Alentejo, and Vinho Verde. The intimate setting features rustic Portuguese tiles, candlelit tables, and warm lighting. Live fado music performances several nights weekly create an emotional, cultural experience. O Fado invites you to discover why Portugal's cuisine remains one of Europe's best-kept culinary secrets." \
  "$$" \
  "4.2" \
  "50"

# Insert Restaurant 8: Grill Masters
insert_restaurant "rest_008" \
  "Grill Masters" \
  "American" \
  "Austin" \
  "222 6th St" \
  "30.2672" \
  "-97.7431" \
  "Grill Masters has earned its reputation as Austin's premier destination for exceptional steaks and fire-cooked specialties, celebrating the art of grilling with passion and expertise. Our chefs are true masters of their craft, possessing deep knowledge of meat selection, dry-aging processes, and grilling techniques refined through years of dedicated practice. We source premium beef from heritage cattle ranches, carefully selecting cuts that offer optimal marbling and flavor. Our steaks are dry-aged in-house for 28-45 days, concentrating flavors and creating that distinctive crust that only high-quality meat can achieve. The open kitchen design allows diners to witness our chefs' artistry as they work over custom-built grills and charcoal fires, creating that authentic smoky aroma that defines great steakhouse dining. Beyond steaks, our menu showcases grilled lamb chops, fresh seafood with perfect char marks, and organic vegetables that taste better kissed by flame. Our sides—from truffle mashed potatoes to grilled asparagus with hollandaise—complement each dish perfectly. The wine list emphasizes bold reds that pair magnificently with grilled proteins. The sophisticated dining room features warm wood, leather seating, and dim lighting that creates an atmosphere of refined indulgence. Our attentive staff provides exemplary service. Grill Masters delivers an unforgettable dining experience." \
  "$$$" \
  "4.9" \
  "70"

# Insert Restaurant 9: Mediterranean Escape
insert_restaurant "rest_009" \
  "Mediterranean Escape" \
  "Mediterranean" \
  "Miami" \
  "333 Ocean Dr" \
  "25.7907" \
  "-80.1300" \
  "Mediterranean Escape captures the essence of seaside dining along the Mediterranean coast, offering fresh, vibrant cuisine with stunning ocean views from Miami Beach. Our restaurant celebrates the culinary traditions spanning Spain, Italy, Greece, Turkey, and the Levant region, each culture contributing distinct flavors and techniques that define Mediterranean gastronomy. Our chef sources the day's catch from local fishermen and Mediterranean importers, crafting daily specials that highlight the season's freshest offerings. The cuisine emphasizes olive oil, fresh vegetables, aromatic herbs, and the finest seafood—prepared simply to let quality ingredients shine. Our menu features wood-fired whole fish, creamy hummus and mezze platters, Greek salads with Feta cheese, Spanish paella made with saffron and fresh seafood, and Italian risottos infused with seasonal flavors. The open-air dining space offers floor-to-ceiling windows framing panoramic ocean vistas, gentle sea breezes, and the sound of waves creating a serene, rejuvenating atmosphere. Our bartenders craft refreshing cocktails using Mediterranean spirits and fresh citrus. The wine collection features selections from coastal regions—Greek Assyrtiko, Spanish Albariño, and Italian Vermentino whites that complement our fresh seafood. Sunset dining is particularly magical. Mediterranean Escape invites you to experience vacation-like bliss through cuisine and ambiance that transports you to sun-drenched Mediterranean shores." \
  "$$" \
  "4.5" \
  "55"

# Insert Restaurant 10: Bangkok Bliss
insert_restaurant "rest_010" \
  "Bangkok Bliss" \
  "Thai" \
  "Los Angeles" \
  "444 Wilshire Blvd" \
  "34.0737" \
  "-118.2713" \
  "Bangkok Bliss transports diners to the vibrant streets and bustling markets of Thailand, offering an authentic culinary journey through regional Thai cuisines prepared with traditional techniques and fresh, authentic ingredients. Our head chef trained in Bangkok under renowned Thai culinary masters, bringing deep expertise in regional specialties from Northern Thailand's herb-forward dishes to Southern Thailand's spicy seafood preparations and Central Thailand's balanced, iconic flavors. Every curry paste is hand-pounded in our kitchen using traditional stone mortars, and coconut milk is freshly pressed daily to ensure maximum flavor. Our menu celebrates Thai diversity—from the aromatic gaeng phed red curry with tender proteins and Thai basil to the delicate green curry with its bright herb flavors, the complex massaman curry with peanuts and warm spices, and the lesser-known jungle curry that tastes of Northern Thailand's forests. Beyond curries, we prepare som tam green papaya salad where our chefs pound ingredients tableside, pad thai with the perfect balance of sweet, sour, salty, and spicy, and fresh spring rolls filled with herbs and proteins. The open kitchen design allows diners to witness the theatrical preparation of dishes—wok flames reaching high and chefs moving in practiced synchronization. Our extensive cocktail menu features Thai spirits and tropical fruits. Bangkok Bliss invites you to experience Thailand's renowned culinary traditions with authenticity and passion." \
  "$$" \
  "4.6" \
  "48"

# Insert Restaurant 11: Churrascaria Rio
insert_restaurant "rest_011" \
  "Churrascaria Rio" \
  "Brazilian" \
  "Denver" \
  "555 Larimer St" \
  "39.7392" \
  "-104.9903" \
  "Churrascaria Rio brings the vibrant energy and flavors of Rio de Janeiro's celebrated churrascarias to Denver. This traditional Brazilian steakhouse celebrates the country's rodízio dining experience, where skilled chefs present an endless procession of perfectly grilled meats carved tableside. Our chefs, trained in Rio's premier churrascarias, masterfully prepare picanha, lamb chops, chicken wrapped in bacon, and specialty cuts using traditional Brazilian grilling techniques over open flames. Every meat is seasoned with a special blend of spices and coarse sea salt, resulting in a flavorful crust and succulent interior. The salad bar features an impressive selection of fresh Brazilian accompaniments, from hearts of palm and exotic fruits to creamy cassava purees and traditional pão de queijo cheese bread. Our wine list showcases premier Brazilian selections. The spacious dining room features warm wood accents, intimate booth seating, and live samba music performances that create an authentic Rio atmosphere. Servers, dressed in traditional Brazilian attire, ensure your glass never empties while continuously presenting an array of perfectly grilled meats. Churrascaria Rio offers a theatrical, unforgettable dining experience celebrating Brazilian hospitality and culinary mastery." \
  "$$$" \
  "4.7" \
  "80"

# Insert Restaurant 12: Seoul Kitchen
insert_restaurant "rest_012" \
  "Seoul Kitchen" \
  "Korean" \
  "Seattle" \
  "666 Capitol Hill" \
  "47.6205" \
  "-122.3212" \
  "Seoul Kitchen authentically represents the bold, complex flavors of Korean cuisine, offering an interactive dining experience that celebrates centuries of culinary tradition. Our head chef, trained in Seoul's most celebrated restaurants, brings expertise in both classical Korean dishes and contemporary fusion interpretations. Every meal begins with banchan, an impressive array of small side dishes that showcase the depth of Korean flavors—from fermented kimchi varieties to seasoned vegetables and marinated proteins. Our signature experience is tableside Korean BBQ, where premium beef and pork are grilled on built-in tabletop grills, allowing diners to perfectly cook their meat while enjoying the ritual and theater of the experience. Beyond BBQ, our menu features bibimbap with perfectly fried eggs and jasmine rice, rich bone broths that simmer for over 24 hours, spicy tteokbokki rice cakes, and delicate japchae glass noodles. We prepare traditional dishes using time-honored techniques, including fermentation processes that develop authentic flavors. Our carefully curated soju collection and Asian beer selection complement the bold, spicy profiles of our cuisine. The intimate, modern dining space features warm lighting and communal seating that encourages connection. Seoul Kitchen invites you to experience Korean cuisine's exciting complexity and convivial dining traditions." \
  "$$" \
  "4.5" \
  "60"

# Insert Restaurant 13: La Taperia Española
insert_restaurant "rest_013" \
  "La Taperia Española" \
  "Spanish" \
  "Miami" \
  "777 Brickell Ave" \
  "25.7617" \
  "-80.1918" \
  "La Taperia Española captures the convivial spirit of Spanish tapas culture, offering an authentic journey through Spain's regional flavors and social dining traditions. Our chef trained in Madrid, Barcelona, and Seville, bringing deep knowledge of Spanish regional cuisines and the art of creating small plates that celebrate quality ingredients and bold flavors. The foundation of our philosophy is sourcing Spain's finest products—jamón ibérico aged for years, Spanish cheeses from various regions, and olive oils from premier producing areas. Our tapas menu showcases Spanish diversity: crispy croquetas filled with creamy jamón and béchamel, patatas bravas with spicy sauce, gambas al ajillo with wild Spanish shrimp and garlic, gildas combining peppers and anchovy, and pulpo a la gallega tender octopus with paprika. We prepare traditional dishes using time-honored techniques, including house-made charcuterie and fresh seafood preparations. Our wine list features Spanish selections from Rioja, Ribera del Duero, and Albariño regions, carefully chosen to pair with our small plates. The lively dining room features exposed brick, warm lighting, and high communal tables that encourage sharing and conversation. Live Spanish guitar performances several evenings weekly create an authentic, romantic atmosphere. La Taperia Española invites you to experience Spanish hospitality through small plates and big flavors." \
  "$$" \
  "4.4" \
  "70"

# Insert Restaurant 14: Sultanahmet Feast
insert_restaurant "rest_014" \
  "Sultanahmet Feast" \
  "Turkish" \
  "Washington DC" \
  "888 H St NW" \
  "38.9072" \
  "-77.0369" \
  "Sultanahmet Feast transports guests to Ottoman Istanbul, celebrating the sophisticated flavors that dominated imperial courts for centuries. Our chef trained in Istanbul's legendary restaurants, bringing expertise in traditional Turkish cuisine and the art of blending Mediterranean and Middle Eastern influences. Every dish reflects the richness of Turkish culinary history—from delicate meze selections including hummus, baba ganoush, and whipped feta, to perfectly grilled lamb kebabs seasoned with carefully balanced spice blends, fresh seafood prepared with Mediterranean herbs, and rich, aromatic lentil soups. We prepare house-made pide and lavash breads in our traditional tandoor oven, creating warm, pillowy perfection. Our signature mezze platter offers a journey through Turkish flavors, while our slow-braised lamb shoulder and grilled whole sea bass showcase our commitment to quality proteins and classical preparation. We craft Turkish coffee with ceremony, and our dessert menu features authentic baklava, Turkish delight, and seasonal fruit preparations. Our carefully selected wine list includes Turkish selections from Anatolia, complementing our complex spice profiles. The elegant dining room features Ottoman-inspired architectural elements, intricate tilework, and warm ambient lighting. Our knowledgeable staff guides guests through Turkish dining traditions. Sultanahmet Feast invites you to experience the sophisticated pleasures of Ottoman culinary heritage." \
  "$$" \
  "4.6" \
  "75"

# Insert Restaurant 15: Cedars of Lebanon
insert_restaurant "rest_015" \
  "Cedars of Lebanon" \
  "Lebanese" \
  "Philadelphia" \
  "999 Market St" \
  "39.9526" \
  "-75.1652" \
  "Cedars of Lebanon celebrates the fresh, vibrant flavors of Lebanese cuisine, offering an authentic Mediterranean dining experience rooted in centuries of Levantine culinary tradition. Our chef, trained in Beirut's finest restaurants, brings expertise in preparing dishes that balance simplicity with sophisticated flavor combinations, emphasizing fresh herbs, citrus, and olive oil. Our extensive meze selection showcases the foundation of Lebanese dining—creamy hummus with warming spices, smoky baba ganoush, tabbouleh bursting with fresh parsley and lemon, fattoush salad with crispy pita chips, and various yogurt-based preparations. Fresh grilled meats and seafood form the heart of our main courses: marinated lamb kebabs, perfectly grilled whole fish with lemon and herbs, and tender grilled chicken with Mediterranean spice blends. We prepare traditional dishes using time-honored techniques, including house-made pastries filled with spinach, cheese, or meat. Fresh-squeezed citrus juices and traditional Lebanese coffee complete the experience. Our wine list features Lebanese selections from the Bekaa Valley, known for their quality and ability to complement our fresh, herb-forward cuisine. The warm, welcoming dining space features rustic wood furnishings, Mediterranean-inspired decor, and soft lighting. Our staff treats guests like family, sharing stories about Lebanese traditions. Cedars of Lebanon invites you to experience the warmth and freshness of Levantine hospitality." \
  "$$" \
  "4.5" \
  "65"

# Insert Restaurant 16: Taverna Santorini
insert_restaurant "rest_016" \
  "Taverna Santorini" \
  "Greek" \
  "Atlanta" \
  "1111 Peachtree St" \
  "33.7490" \
  "-84.3880" \
  "Taverna Santorini captures the sun-washed charm and Mediterranean flavors of Greece's iconic island, offering an authentic taste of Greek hospitality and culinary excellence. Our chef, trained in Athens and the Greek islands, brings deep knowledge of regional Greek cuisines and commitment to using Greece's celebrated ingredients. Every dish celebrates Mediterranean simplicity—grilled branzino and octopus prepared with just olive oil and lemon, creamy saganaki cheese fried tableside, lamb prepared with traditional Greek herbs and spices, and fresh vegetables grilled to perfection. We prepare traditional dishes using time-honored techniques passed through generations, from slow-braised rabbit stifado to tender lamb keftedes, fresh spanakopita spinach pies, and creamy melitzanosalata. Our mezze selections showcase Greek staples: creamy feta cheese, briny olives, fresh tomato and cucumber, crispy saganaki, and grilled shrimp. Fresh pasta prepared in-house, slow-roasted lamb, and daily fresh fish specials highlight our commitment to quality ingredients. Our wine list features premier Greek selections from Santorini, Crete, and mainland regions, all chosen to complement our Mediterranean cuisine. The charming dining room features whitewashed walls, blue accents reminiscent of island homes, and soft candlelight. Bouzouki music and the warmth of Greek hospitality create an inviting atmosphere. Taverna Santorini invites you to escape to the Greek islands." \
  "$$" \
  "4.7" \
  "72"

# Insert Restaurant 17: Pho Vietnam
insert_restaurant "rest_017" \
  "Pho Vietnam" \
  "Vietnamese" \
  "Houston" \
  "1212 Westheimer Rd" \
  "29.7604" \
  "-95.3698" \
  "Pho Vietnam authentically represents the fresh, balanced flavors of Vietnamese cuisine, celebrating the country's culinary heritage through traditional preparations and quality ingredients. Our head chef trained in Hanoi and Ho Chi Minh City, bringing expertise in creating broths that simmer for 24 hours, hand-pulled fresh noodles, and dishes that balance sweet, sour, salty, and spicy elements. The heart of our menu is our signature pho—aromatic beef or chicken broth infused with star anise, cinnamon, and other warming spices, served with fresh rice noodles and a selection of herbs and proteins. We prepare our broths using traditional techniques, simmering beef bones with charred onions and ginger to create deep, complex flavors. Beyond pho, we offer bun cha with charred pork and fresh herbs, bánh mì sandwiches with perfectly balanced flavors, spring rolls both fresh and fried, and stir-fried dishes bursting with authentic flavors. Our fresh herb selection is exceptional—Thai basil, cilantro, Vietnamese mint—allowing you to customize each dish to preference. Fresh lime, chiles, and fish sauce add finishing touches. Our beverage menu features Vietnamese coffee, traditional iced tea, and sugarcane juice. The casual, welcoming dining space features traditional Vietnamese artwork and warm lighting. Our knowledgeable staff guides you through Vietnamese dining traditions. Pho Vietnam invites you to experience authentic Vietnamese flavors." \
  "$" \
  "4.4" \
  "50"

# Insert Restaurant 18: Asador Argentino
insert_restaurant "rest_018" \
  "Asador Argentino" \
  "Argentinian" \
  "Las Vegas" \
  "1313 S Las Vegas Blvd" \
  "36.1699" \
  "-115.1398" \
  "Asador Argentino celebrates the legendary steaks and passionate culinary traditions of Argentina, offering a premium grilling experience that showcases South America's finest beef. Our chef trained in Buenos Aires' most celebrated asadores, bringing expertise in sourcing Argentinian beef and mastering the art of grilling over open flames and wood fires. We source premium grass-fed beef from Argentinian ranches, selecting cuts known for superior flavor and tenderness—ribeye, tomahawk, strip steak, and the iconic Argentinian asado cuts. Our grilling philosophy honors simplicity: premium beef, quality salt, and perfectly controlled fire create dishes of unparalleled flavor. Beyond beef, we grill lamb, pork, and fresh seafood with the same attention to technique and ingredient quality. We prepare traditional Argentinian dishes including chimichurri sauce made fresh daily with Italian parsley and spices, crispy empanadas filled with beef and spices, and tender grillos marinated in wine and herbs. Our wine list showcases premier Argentinian selections from Mendoza and Salta regions, known for bold Malbecs that pair beautifully with grilled meats. The sophisticated dining room features an open kitchen where you can witness skilled chefs working the grill, creating that authentic asador atmosphere. Warm wood finishes and soft lighting create an intimate setting. Our knowledgeable staff shares Argentinian traditions. Asador Argentino invites you to experience authentic Argentine grilling excellence." \
  "$$$" \
  "4.8" \
  "85"

# Insert Restaurant 19: Riad Marrakech
insert_restaurant "rest_019" \
  "Riad Marrakech" \
  "Moroccan" \
  "Phoenix" \
  "1414 Camelback Rd" \
  "33.4484" \
  "-112.0742" \
  "Riad Marrakech transports guests to the enchanting markets and palatial homes of Morocco, celebrating the country's exotic spice blends and ancient culinary traditions. Our chef trained in Marrakech and Fez, bringing expertise in preparing authentic Moroccan dishes featuring warming spices, dried fruits, and bold flavors that reflect the country's Berber, Arab, and French influences. Every meal celebrates Moroccan hospitality and the art of slow cooking. Our tagine preparations showcase our philosophy—tender lamb or chicken cooked with preserved lemons, olives, and warming spices like cinnamon, cumin, and ginger, served in traditional pottery vessels. We prepare couscous with carefully layered flavors, house-made phyllo pastries filled with chicken and almonds dusted with cinnamon sugar, and slow-braised beef with prunes and apricots. Our appetizer selection includes creamy hummus, smoky baba ganoush, fresh salads with cumin-spiced dressing, and flaky pastilla pastries. Fresh-squeezed orange juice, traditional Moroccan mint tea, and house-made desserts complete the experience. Our wine list features Moroccan selections from various regions. The dining room features riad-style architecture with intricate tile work, carved plaster walls, and soft lantern lighting creating intimate spaces. Traditional Moroccan music and the aroma of warming spices fill the air. Our staff, dressed in traditional attire, provides warm hospitality. Riad Marrakech invites you to experience Morocco's culinary magic." \
  "$$" \
  "4.6" \
  "68"

# Insert Restaurant 20: Cevicheria Lima
insert_restaurant "rest_020" \
  "Cevicheria Lima" \
  "Peruvian" \
  "San Diego" \
  "1515 Gaslamp Quarter" \
  "32.7157" \
  "-117.1611" \
  "Cevicheria Lima celebrates the vibrant coastal flavors of Peru, showcasing the country's diverse ingredients and culinary innovations that have earned Peru recognition as a gastronomic destination. Our chef trained in Lima's celebrated restaurants, bringing expertise in preparing ceviche—the national dish—and other fresh seafood preparations that define Peruvian coastal cuisine. The heart of our menu is ceviche, prepared with the day's freshest fish, citrus juices, chiles, and aromatics, each variation telling a story of Peru's diverse regions and seafood traditions. We prepare traditional ceviche with white fish, but also showcase seasonal variations with octopus, mussels, and mixed seafood, each with distinctive flavor profiles. Beyond ceviche, we offer causas—creamy layers of potato and avocado topped with marinated seafood, fresh ceviche served in crispy wonton cups, and tiradito—thinly sliced raw fish with citrus and spice. Our main courses feature grilled fish with Peruvian herbs, seafood stews bursting with coastal flavors, and traditional dishes like ají de gallina with creamy nut sauce and chicken. We prepare fresh salsas and ceviches throughout the day. Pisco-based cocktails showcase Peru's renowned brandy, while our wine list features Peruvian selections. The bright, modern dining space features coastal-inspired decor and open kitchen design. Our knowledgeable staff shares Peruvian traditions. Cevicheria Lima invites you to experience Peru's dynamic coastal cuisine." \
  "$$" \
  "4.7" \
  "58"

# Insert Restaurant 21: Hyderabad House
insert_restaurant "rest_021" \
  "Hyderabad House" \
  "Indian" \
  "Austin" \
  "1616 Congress Ave" \
  "30.2672" \
  "-97.7431" \
  "Hyderabad House celebrates the unique and aromatic flavors of Hyderabadi cuisine, a culinary tradition from South India known for its use of nuts, dried fruits, and complex spice blends. Our head chef trained in Hyderabad, bringing authentic expertise in preparing the region's signature dishes with traditional cooking methods passed down through generations. The heart of our menu is our legendary Hyderabadi biryani—basmati rice layered with marinated meat, fried onions, and whole spices, slow-cooked in sealed vessels to create aromatic perfection with each grain infused with flavor. We prepare various biryani styles: chicken, lamb, goat, and vegetarian versions, each with distinctive spice profiles and cooking techniques. Beyond biryani, we offer Hyderabadi specialties including haleem—meat cooked with lentils and wheat until creamy and textured, kebabs marinated in yogurt and traditional spices, and curries that balance heat with aromatic complexity. Our signature Hyderabadi dum pukht preparation involves slow-cooking meats in their own juices with precise spice control, creating incomparable tenderness and depth. We prepare traditional halwas and kheer desserts using techniques refined over centuries. Our beverage selection features Indian wines, craft cocktails infused with traditional spices, and traditional Indian lassi. The warm, inviting dining space features traditional Hyderabadi artwork and ambient lighting. Our knowledgeable staff shares stories of Hyderabad's culinary heritage. Hyderabad House invites you to experience South India's most treasured flavors." \
  "$$" \
  "4.6" \
  "62"

# Insert Restaurant 22: Bier Garten
insert_restaurant "rest_022" \
  "Bier Garten" \
  "German" \
  "Denver" \
  "1717 Speer Blvd" \
  "39.7489" \
  "-104.9870" \
  "Bier Garten brings the festive warmth and hearty flavors of Bavarian beer hall culture to Denver, celebrating Germany's centuries-old culinary traditions and convivial dining atmosphere. Our chef trained in Munich, bringing authentic expertise in preparing traditional German dishes with regional variations from Bavaria, Swabia, and the Rhineland. Our menu showcases hearty German classics: perfectly prepared schnitzel with traditional toppings, authentically spiced bratwurst and other sausages sourced from our partner butcher, tender sauerbraten slow-braised in vinegar and spices, and creamy spätzle egg noodles. We prepare traditional German bread soups, creamy mushroom sauces, and red cabbage with apples using recipes refined over generations. Our pretzel selection is exceptional—warm, chewy pretzels with traditional salt and soft warm pretzels served with mustard. We offer traditional German charcuterie and cheese boards featuring imports from various German regions. Our beer selection is extraordinary—over 60 German beers from breweries across Bavaria, including wheat beers, pilsners, and dark lagers. The authentic beer hall atmosphere features long communal wooden tables, traditional Bavarian decorations, and live accordion music on select evenings. Our staff, dressed in traditional German attire, provides warm hospitality and recommends perfect beer pairings. Bier Garten invites you to experience authentic German celebration and cuisine." \
  "$$" \
  "4.5" \
  "90"

# Insert Restaurant 23: Norden
insert_restaurant "rest_023" \
  "Norden" \
  "Scandinavian" \
  "Minneapolis" \
  "1818 Hennepin Ave" \
  "44.9889" \
  "-93.2723" \
  "Norden celebrates the elegant minimalism and bold flavors of Nordic cuisine, representing culinary traditions from Sweden, Norway, Denmark, and Finland that emphasize pristine ingredients and refined techniques. Our chef trained in Copenhagen and Stockholm, bringing expertise in the New Nordic movement that honors traditional preparation methods while embracing contemporary approaches. Our philosophy centers on seasonal ingredients prepared with minimal intervention to highlight natural flavors—fresh seafood from Nordic waters prepared with just salt, herbs, and high-quality oils, locally sourced vegetables transformed into elegant preparations, and heritage grains and legumes thoughtfully incorporated. Our menu features cured and smoked fish traditions, including gravlax and various smoked preparations, perfectly prepared seafood showcasing Nordic waters, traditional meatball preparations elevated with fine technique, and vegetable-forward dishes that celebrate seasonal availability. We prepare traditional Nordic breads using sourdough cultures, root vegetables with warming spices, and creamy sauces made with Nordic dairy and traditional methods. Our dessert selection honors Scandinavian traditions with carefully crafted pastries, berry preparations, and traditional sweets. Our beverage list features Nordic craft beers, aquavit selections, and carefully chosen wines. The minimalist dining room features light woods, large windows, and clean Scandinavian design elements that create an inviting, sophisticated atmosphere. Our knowledgeable staff shares Nordic culinary traditions. Norden invites you to experience the refined elegance of Nordic cuisine." \
  "$$$" \
  "4.8" \
  "55"

# Insert Restaurant 24: Fondue Lodge
insert_restaurant "rest_024" \
  "Fondue Lodge" \
  "Swiss" \
  "Salt Lake City" \
  "1919 S Temple" \
  "40.7580" \
  "-111.8910" \
  "Fondue Lodge celebrates the intimate, convivial traditions of Swiss alpine dining, featuring iconic cheese fondues, meat fondues, and chocolate preparations that define Swiss culinary culture. Our chef trained in Zurich and the Swiss Alps, bringing authentic expertise in preparing traditional fondue dishes using premium Swiss cheeses and time-honored techniques. The heart of our experience is our signature cheese fondues—creamy blends of Emmental, Gruyère, and Appenzell cheeses combined with white wine, kirsch, and nutmeg, created tableside in traditional cast-iron pots, bubbling gently as you dip bread cubes and vegetables. We offer variations including traditional Swiss fondue, alpine herb-infused versions, and seasonal preparations. Beyond cheese, we prepare traditional raclette—melted cheese scraped onto bread and potatoes with traditional accompaniments—and fondue bourguignonne, where prime beef is cooked in hot oil at your table. Our menu features Swiss specialties including rösti hash browns with various toppings, veal dishes prepared with traditional alpine herbs, and Swiss-style sausages. We conclude meals with chocolate fondue featuring premium Swiss chocolate with strawberries, banana, and marshmallows for dipping. Our wine list features Swiss selections from various regions, with emphasis on wines pairing beautifully with cheese. The cozy, intimate dining space features alpine lodge aesthetics, warm lighting, and private booths perfect for fondue dining. Our attentive staff ensures perfect temperature and technique throughout your fondue experience. Fondue Lodge invites you to experience Swiss alpine hospitality." \
  "$$$" \
  "4.7" \
  "48"

# Insert Restaurant 25: Magyar Kitchen
insert_restaurant "rest_025" \
  "Magyar Kitchen" \
  "Hungarian" \
  "Chicago" \
  "2020 W Division St" \
  "41.9039" \
  "-87.6743" \
  "Magyar Kitchen celebrates the rich, warming flavors of Hungarian cuisine, honoring centuries of culinary tradition that reflects influences from various Central European cultures. Our head chef trained in Budapest, bringing authentic expertise in preparing Hungary's signature dishes with traditional cooking methods and spice blends refined over generations. The foundation of Hungarian cuisine is paprika—we use premium Hungarian paprika in various forms to create complex, layered flavors throughout our menu. Our iconic goulash, prepared with tender beef, onions, and paprika, simmers for hours creating rich, warming perfection. We prepare traditional Hungarian specialties including chicken paprikash with creamy sour cream sauce, beef stew with mushrooms and traditional herbs, and schnitzels prepared with Hungarian technique. Our menu features traditional soups including hearty bean soups and lighter vegetable preparations. We prepare traditional Hungarian dumplings and egg noodles with various accompaniments, tender pork preparations, and fresh seafood prepared with Hungarian spice. Our pastry selection showcases Hungarian traditions: flaky strudel filled with apples and cherries, poppy seed cake, and traditional dobos torte with caramel layers. Our wine list features Hungarian selections from Tokaj and other regions, with emphasis on wines complementing our bold, warming flavors. The rustic, welcoming dining space features traditional Hungarian artwork and warm, inviting lighting. Our staff shares Hungarian cultural traditions. Magyar Kitchen invites you to experience authentic Hungarian comfort and hospitality." \
  "$$" \
  "4.5" \
  "68"

# Insert Restaurant 26: Krakow House
insert_restaurant "rest_026" \
  "Krakow House" \
  "Polish" \
  "Columbus" \
  "2121 N High St" \
  "40.0081" \
  "-83.0014" \
  "Krakow House celebrates the hearty, soul-warming traditions of Polish cuisine, honoring generations of culinary heritage that reflects Poland's rich history and agricultural bounty. Our chef trained in Warsaw and Krakow, bringing authentic expertise in preparing traditional Polish dishes using time-honored techniques and quality ingredients sourced from Polish suppliers. Our menu showcases iconic Polish comfort foods: perfectly prepared pierogi filled with potato and cheese, sauerkraut and mushroom, or meat preparations, served with caramelized onions and sour cream. We prepare traditional bigos—a hunter's stew with various meats and vegetables slow-cooked in wine and spices until flavors meld into warming complexity. Our menu features barszcz, a beet soup served with traditional accompaniments, creamy mushroom soups, and hearty vegetable preparations. We offer traditional Polish sausages and kielbasa prepared with authentic recipes, tender pork preparations including traditional Polish-style breaded cutlets, and slow-braised beef dishes. Our piernik gingerbread cake, sernik cheesecake, and paczki jelly-filled pastries showcase Polish pastry traditions. We prepare traditional Polish dumplings and egg noodles with various savory and sweet accompaniments. Our beverage selection features Polish vodkas and beers, particularly craft selections highlighting Polish brewing traditions. The warm, welcoming dining space features traditional Polish decorations and folk artwork, creating an inviting, nostalgic atmosphere. Our staff shares Polish cultural traditions and stories. Krakow House invites you to experience authentic Polish warmth and hospitality." \
  "$$" \
  "4.4" \
  "60"

# Insert Restaurant 27: Volga
insert_restaurant "rest_027" \
  "Volga" \
  "Russian" \
  "Detroit" \
  "2222 W Lafayette" \
  "42.3314" \
  "-83.0899" \
  "Volga celebrates the rich, complex flavors of Russian cuisine, honoring culinary traditions that reflect Russia's diverse regions and centuries of cultural heritage. Our chef trained in Moscow and St. Petersburg, bringing authentic expertise in preparing traditional Russian dishes using techniques and ingredients that define Russian gastronomy. Our menu showcases iconic Russian classics: beef stroganoff with tender beef and creamy mushroom sauce, perfectly prepared chicken Kiev with butter-filled center, and traditional pelmeni dumplings filled with meat and herbs. We prepare borscht—a legendary beet soup—with various accompaniments and seasonal variations, creamy mushroom soup traditionally served with sour cream and dill, and vegetable soups reflecting Russian culinary traditions. Our menu features traditional Russian sausages and cured meats, slow-braised beef preparations, and tender chicken dishes prepared with warming spices. We offer traditional Russian piroshki pastries filled with meat, vegetables, or jam, and open-faced sandwiches with various toppings. Our dessert selection includes medovik honey cake, syrniki pancakes with sour cream, and traditional Russian pastries. We prepare blini pancakes served with caviar, sour cream, or sweet accompaniments. Our beverage selection features Russian vodkas, craft selections, and traditional beverages. The elegant, classic dining space features Russian artwork and warm, sophisticated lighting. Our staff shares Russian cultural traditions and stories. Volga invites you to experience the warmth and richness of Russian hospitality." \
  "$$" \
  "4.6" \
  "70"

# Insert Restaurant 28: Lumpia Palace
insert_restaurant "rest_028" \
  "Lumpia Palace" \
  "Filipino" \
  "Queens" \
  "2323 Roosevelt Ave" \
  "40.7614" \
  "-73.9200" \
  "Lumpia Palace celebrates the vibrant, diverse flavors of Filipino cuisine, a culinary tradition that blends Spanish, Chinese, Malaysian, and Indigenous influences into uniquely Filipino preparations. Our chef trained in Manila, bringing authentic expertise in preparing traditional Filipino dishes with techniques refined through generations and accessible to Filipino communities worldwide. Our menu celebrates Filipino favorites: perfectly fried lumpia spring rolls with various fillings, adobo slow-braised meats in savory sauce, and sinigang pork stew with tamarind and vegetables. We prepare kinilaw—Philippine ceviche with fresh fish cured in vinegar and citrus with aromatic herbs—and various seafood preparations honoring Philippines' rich maritime traditions. Our menu features dinuguan—blood stew with bold, savory flavors—lechon preparations, Filipino-style grilled meats with special sauces, and pancit noodles with various accompaniments. We offer traditional desserts including leche flan with silky caramel sauce, halo-halo shaved ice with beans and condensed milk, and bibingka rice cake. Fresh tropical fruit preparations and traditional sweets showcase Filipino agricultural bounty. Our beverage selection features Filipino beers, exotic fruit juices, and tropical beverages. The lively, welcoming dining space features Filipino artwork and warm, festive lighting. Our staff shares Filipino cultural traditions and warmly welcomes guests. Lumpia Palace invites you to experience the joyful, flavor-rich traditions of Filipino cuisine." \
  "$" \
  "4.5" \
  "65"

# Insert Restaurant 29: Rendang Rijstaffel
insert_restaurant "rest_029" \
  "Rendang Rijstaffel" \
  "Indonesian" \
  "Portland" \
  "2424 SE Hawthorne" \
  "45.5159" \
  "-122.6503" \
  "Rendang Rijstaffel celebrates the complex, aromatic flavors of Indonesian cuisine, a culinary tradition spanning thousands of islands with diverse ingredients, techniques, and flavor profiles. Our chef trained in Jakarta and Bali, bringing authentic expertise in preparing traditional Indonesian dishes using spice pastes and cooking methods perfected over centuries. The heart of our experience is rijstaffel—the traditional Indonesian rice table featuring an array of complementary dishes served with steamed rice, creating a harmonious, multi-course dining experience. Our rendang preparations—meats slow-cooked in coconut milk with complex spice pastes until sauce reduces and coats proteins—showcase Indonesian culinary mastery. We prepare traditional soto soups with aromatic spices and herbs, sambal preparations ranging from mild to intensely spicy, and gado-gado vegetable salad with peanut sauce. Our menu features satay skewers with complex sauce, spring rolls with various fillings, and fresh seafood preparations honoring Indonesia's maritime traditions. We prepare traditional cassava cake, sticky rice with mango, and tropical fruit preparations. Fresh coconut milk, aromatic spices, and traditional preparation methods define our authentic approach. Our beverage selection features Indonesian beverages, tropical fruit juices, and craft selections. The warm, inviting dining space features Indonesian artwork and soft, ambient lighting. Our knowledgeable staff guides you through Indonesian culinary traditions. Rendang Rijstaffel invites you to experience Indonesia's spectacular culinary diversity." \
  "$$" \
  "4.7" \
  "72"

# Insert Restaurant 30: Teppan Masters
insert_restaurant "rest_030" \
  "Teppan Masters" \
  "Japanese" \
  "Dallas" \
  "2525 McKinney Ave" \
  "32.7919" \
  "-96.8003" \
  "Teppan Masters celebrates the theatrical artistry and refined flavors of Japanese teppanyaki cuisine, where skilled chefs prepare dishes with precision and showmanship directly in front of diners at interactive steel griddles. Our chefs trained in Tokyo, bringing years of expertise in teppanyaki techniques, Japanese knife skills, and the art of entertaining while preparing exceptional food. Our signature experience features premium Japanese beef, fresh seafood, and seasonal vegetables cooked to perfection on sizzling teppanyaki griddles with theatrical knife work and skillful plating. We source only the finest ingredients: Japanese A5 wagyu beef with exceptional marbling, pristine fresh seafood including shrimp and scallops, and seasonal vegetables prepared with precision. Our chefs perform synchronized cooking routines, creating onion volcanoes, egg fried rice in entertaining patterns, and precisely grilled proteins finished with signature sauces. Beyond teppanyaki, we offer traditional Japanese sushi and sashimi prepared by master sushi chefs, Japanese appetizers, and authentic side dishes. We prepare traditional Japanese soups and salads with careful attention to balance and presentation. Our sake selection features premium Japanese selections from various regions, curated to pair beautifully with grilled preparations. The sophisticated dining space features teppanyaki counters where you sit directly in front of skilled chefs, creating an interactive, entertaining dining experience. Our staff provides exceptional service. Teppan Masters invites you to experience Japanese culinary artistry and entertainment." \
  "$$$" \
  "4.8" \
  "80"

echo ""
echo "✅ All 30 synthetic restaurant records have been successfully inserted!"
