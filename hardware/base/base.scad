// Define dimensions. All in mm

num_cams = 7;
plate_thickness = 3.5; // thickness of base plate
mid_thickness = 3.5; // Thickness of inner raised area (first "step")
edge_thickness = 7; // Thickness of the raised edge where the holes are
edge_width_from_hole = 4; // Width of the edge, material on each side of the hole
hole_diameter = 4.75; 
radius_to_hole = 65; // Distance from center to the center of the mounting holes
mid_area_width = 5; // Width of the inner raised area
radius_central_gap = 60 ; // Radius of the empty central area

// Alignment indent in edge
picam_base_width = 20; 
picam_base_thickness = 10;
indent_depth = 3;
offset_of_hole = 0; // If the mounting bolt hole isn't centered you can adjust it

// Don't touch
rotate_angle = 360/num_cams;
overhang = edge_width_from_hole + hole_diameter/2;
plate_length = radius_to_hole + overhang;
poly_side = tan(360/(num_cams * 2)) * 2 * (plate_length);
radius_to_cam_base = radius_to_hole - picam_base_thickness / 2 - offset_of_hole;

// Main loop            
union(){
for (cam = [1 : num_cams]){
    rotate([0, 0, cam * rotate_angle]){
        difference(){
            union(){
                translate([radius_central_gap, -poly_side / 2, 0]){
                    cube([plate_length - radius_central_gap, poly_side, plate_thickness]);
                }
                translate([radius_to_hole - overhang,-poly_side / 2,0]){
                    cube([overhang * 2, poly_side, edge_thickness]);
                }
                translate([radius_to_hole - overhang - mid_area_width, -poly_side / 2, 0]){
                    cube([mid_area_width, poly_side, mid_thickness]);
                }
            }
            translate([radius_to_hole, 0, -1]){
                cylinder(r = hole_diameter / 2, h = edge_thickness + 2, $fn = 64);
            }
            translate([radius_to_cam_base, -picam_base_width/2, edge_thickness - indent_depth]){
                cube([picam_base_thickness, picam_base_width, indent_depth + 1]);
            }
        }
    }
}
}