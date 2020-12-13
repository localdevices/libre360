// Define dimensions. All in mm

num_cams = 7;

//mid_thickness = 7; // Thickness of inner raised area (first "step")
edge_thickness = 7; // Thickness of the raised edge where the holes are
edge_width_from_hole = 7; // Width of the edge, material on each side of the hole
hole_diameter = 6; // bolt hole diameter
bolthead_d = 10; // bolt head countersink diameter
bolthead_h = 2; // bolt head height (for countersink depth)
radius_to_hole = 50; // Distance from center to the center of the mounting holes
//mid_area_width = 0; // Width of the inner raised area
radius_central_gap = 8.75  ; // Radius of the empty central area
central_gap_thickness = 12.7;
downangle = 25; // Angle in degrees cameras face downward


// Alignment indent in edge
// picam base width is 13.5
picam_base_width = 14.1375 ; 
// picam base thickness is 11.5, optimum size is
// 12.1375, but we want to give a little space for
// bad drilling and it's better to index against
// the side
picam_base_thickness = 12.2;
indent_depth = 4;
offset_of_hole = 0; // If the mounting bolt hole isn't centered you can adjust it
plate_thickness = edge_thickness - indent_depth; // thickness of base plate

// Don't touch
rotate_angle = 360/num_cams;
overhang = edge_width_from_hole + hole_diameter/2;
plate_length = radius_to_hole + overhang;
poly_side = tan(360/(num_cams * 2)) * 2 * (plate_length);
plate_length_hole = radius_central_gap;
poly_side_hole = tan(360/(num_cams * 2)) * 2 * (plate_length_hole);
radius_to_cam_base = radius_to_hole - picam_base_thickness / 2 - offset_of_hole;

// Part
difference(){
    // Body loop
    for (cam = [1 : num_cams]){
        rotate([0, 0, cam * rotate_angle]){
            union(){
                translate([radius_central_gap, -poly_side / 2, 0]){
                    cube([plate_length - radius_central_gap, poly_side, plate_thickness]);
                }
                // Spokes
                translate([radius_central_gap,-poly_side_hole / 2,0]){
                    cube([overhang, poly_side, edge_thickness]);
                }
                // Wheel
                translate([radius_to_hole - overhang,-poly_side / 2,0]){
                    cube([overhang * 2, poly_side, edge_thickness]);
                }
            }
        }
    }
    // Camera mount holes loop
    for (cam = [1 : num_cams]){

	 
        rotate([0,0,cam * rotate_angle + (360/num_cams/1.8)]){
            translate([radius_to_hole, -picam_base_width/2, edge_thickness - indent_depth]){
                rotate([0, downangle, -rotate_angle]){
                    union(){
                        translate([-picam_base_thickness / 2, -picam_base_width / 2, 0]){
                            cube([picam_base_thickness, picam_base_width, indent_depth + 10]);
                        }
                        translate([0, 0, -(bolthead_h * 2 + 10)]){
                            cylinder(r = hole_diameter / 2, h = edge_thickness * 3 + 10, $fn = 64);
                            cylinder(r = bolthead_d / 2 + 0.1, h = bolthead_h + 10, $fn = 64);

                        }
                    }
                }
            }
        }
    }
}
