-- Fix partner image paths: .png/.jpeg -> .jpg
-- Generated after batch resize of static/partners images.
-- Each UPDATE matches on the old path value for safety.

-- logo_image updates
UPDATE book_partner SET logo_image = 'partners/logo_bootlegger.jpg'                                        WHERE logo_image = 'partners/logo_bootlegger.png';
UPDATE book_partner SET logo_image = 'partners/logo_krispy_kreme.jpg'                                      WHERE logo_image = 'partners/logo_krispy_kreme.png';
UPDATE book_partner SET logo_image = 'partners/logo_mugg_bean.jpg'                                         WHERE logo_image = 'partners/logo_mugg_bean.png';
UPDATE book_partner SET logo_image = 'partners/logo_spur.jpg'                                              WHERE logo_image = 'partners/logo_spur.png';
UPDATE book_partner SET logo_image = 'partners/logo_starbucks.jpg'                                         WHERE logo_image = 'partners/logo_starbucks.png';
UPDATE book_partner SET logo_image = 'partners/logo_vida_e.jpg'                                            WHERE logo_image = 'partners/logo_vida_e.png';
UPDATE book_partner SET logo_image = 'partners/logo_wimpy.jpg'                                             WHERE logo_image = 'partners/logo_wimpy.png';
UPDATE book_partner SET logo_image = 'partners/logo_adventure_golf.jpg'                                    WHERE logo_image = 'partners/logo_adventure_golf.png';
UPDATE book_partner SET logo_image = 'partners/logo_animal_farm_yard.jpg'                                  WHERE logo_image = 'partners/logo_animal_farm_yard.png';
UPDATE book_partner SET logo_image = 'partners/logo_blasters_family_entertainment_centre.jpg'              WHERE logo_image = 'partners/logo_blasters_family_entertainment_centre.png';
UPDATE book_partner SET logo_image = 'partners/logo_bounce.jpg'                                            WHERE logo_image = 'partners/logo_bounce.png';
UPDATE book_partner SET logo_image = 'partners/logo_bushwhacked_outdoor_adventures.jpg'                    WHERE logo_image = 'partners/logo_bushwhacked_outdoor_adventures.png';
UPDATE book_partner SET logo_image = 'partners/logo_butterfly_valley.jpg'                                  WHERE logo_image = 'partners/logo_butterfly_valley.png';
UPDATE book_partner SET logo_image = 'partners/logo_ceres_zipline_adventures.jpg'                          WHERE logo_image = 'partners/logo_ceres_zipline_adventures.png';
UPDATE book_partner SET logo_image = 'partners/logo_cheetah_experience.jpg'                                WHERE logo_image = 'partners/logo_cheetah_experience.png';
UPDATE book_partner SET logo_image = 'partners/logo_clubventure_zipline_tours.jpg'                         WHERE logo_image = 'partners/logo_clubventure_zipline_tours.png';
UPDATE book_partner SET logo_image = 'partners/logo_creative_dance_academy.jpg'                            WHERE logo_image = 'partners/logo_creative_dance_academy.png';
UPDATE book_partner SET logo_image = 'partners/logo_dna_paintball.jpg'                                     WHERE logo_image = 'partners/logo_dna_paintball.png';
UPDATE book_partner SET logo_image = 'partners/logo_gravity_trampoline_park.jpg'                           WHERE logo_image = 'partners/logo_gravity_trampoline_park.png';
UPDATE book_partner SET logo_image = 'partners/logo_hunyani_snake_city.jpg'                                WHERE logo_image = 'partners/logo_hunyani_snake_city.png';
UPDATE book_partner SET logo_image = 'partners/logo_imhoff_snake_and_reptile_rehabilitation_centre.jpg'    WHERE logo_image = 'partners/logo_imhoff_snake_and_reptile_rehabilitation_centre.png';
UPDATE book_partner SET logo_image = 'partners/logo_johannesburg_zoo.jpg'                                  WHERE logo_image = 'partners/logo_johannesburg_zoo.png';
UPDATE book_partner SET logo_image = 'partners/logo_jump_street.jpg'                                       WHERE logo_image = 'partners/logo_jump_street.png';
UPDATE book_partner SET logo_image = 'partners/logo_jumpers_lane.jpg'                                      WHERE logo_image = 'partners/logo_jumpers_lane.png';
UPDATE book_partner SET logo_image = 'partners/logo_moholoholo_animal_rehabilitation_centre.jpg'           WHERE logo_image = 'partners/logo_moholoholo_animal_rehabilitation_centre.png';
UPDATE book_partner SET logo_image = 'partners/logo_nu_metro.jpg'                                          WHERE logo_image = 'partners/logo_nu_metro.png';
UPDATE book_partner SET logo_image = 'partners/logo_rush.jpg'                                              WHERE logo_image = 'partners/logo_rush.png';
UPDATE book_partner SET logo_image = 'partners/logo_s_w_a_t_laser_tag.jpg'                                 WHERE logo_image = 'partners/logo_s_w_a_t_laser_tag.png';
UPDATE book_partner SET logo_image = 'partners/logo_saddle_creek_adventures.jpg'                           WHERE logo_image = 'partners/logo_saddle_creek_adventures.png';
UPDATE book_partner SET logo_image = 'partners/logo_splash_jump_zone.jpg'                                  WHERE logo_image = 'partners/logo_splash_jump_zone.png';
UPDATE book_partner SET logo_image = 'partners/logo_total_ninja.jpg'                                       WHERE logo_image = 'partners/logo_total_ninja.png';
UPDATE book_partner SET logo_image = 'partners/logo_valley_crag.jpg'                                       WHERE logo_image = 'partners/logo_valley_crag.png';
UPDATE book_partner SET logo_image = 'partners/logo_wild_x_adventure.jpg'                                  WHERE logo_image = 'partners/logo_wild_x_adventure.png';

-- landing_image updates
UPDATE book_partner SET landing_image = 'partners/landing_vida_e.jpg'      WHERE landing_image = 'partners/landing_vida_e.png';
UPDATE book_partner SET landing_image = 'partners/landing_wimpy.jpg'       WHERE landing_image = 'partners/landing_wimpy.jpeg';
UPDATE book_partner SET landing_image = 'partners/landing_acrobranch.jpg'  WHERE landing_image = 'partners/landing_acrobranch.png';
UPDATE book_partner SET landing_image = 'partners/landing_dna_paintball.jpg' WHERE landing_image = 'partners/landing_dna_paintball.png';
UPDATE book_partner SET landing_image = 'partners/landing_ijump.jpg'       WHERE landing_image = 'partners/landing_ijump.png';
UPDATE book_partner SET landing_image = 'partners/landing_nu_metro.jpg'    WHERE landing_image = 'partners/landing_nu_metro.png';
