// Define dimensions. All in mm

num_cams = 8;

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
downangle = 32; // Angle in degrees cameras face downward


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

module picam(){
    translate([12,14,0]){
        rotate([0, 0, 90 ]){
            import("raspicam.stl", convexity=10);
        }
    }
}

//picam();

module lens() {
    translate([12,14,0]){
        rotate([0, 0, 90 ]){
            union(){
                // Lens
                translate([0,0,30]){
                    rotate([90,0,0]) 
                        {cylinder(r=22.8832/2, h=36);}
                    }

                // Cone of lens view
                
                translate([0,-25,30]){
                    rotate([90,0,0]) 
                        {cylinder(r1=0, r2=45.568/2*4, h=19.727*4);}
                    }    
                
                }
            }
        }
}

// Holy Cameras Batman
// Camera lens loop
module camera_holes() {
    for (cam = [1 : num_cams]){
        rotate([0,0,cam * rotate_angle + (360/num_cams/1.8)]){
            translate([radius_to_hole, -picam_base_width/2, edge_thickness - indent_depth]){
                rotate([0, downangle, rotate_angle ]){
                    union(){
                        translate([-picam_base_thickness / 2, -picam_base_width / 2, 0]){
                            //picam();
                            lens();
                        }
                    }
                }
            }
        }
    }
}

num_sides = 36;
rotate_angle_sides = 360/num_sides;

module stringer() {
    scale([0.234,0.234,0.234]) {
        translate([-225,0,0]){
            rotate([0, 90, 0]){    
                rotate_extrude(angle = 180, $fn = 100, convexity = 20) {

                        rotate([0, 0, 90]){
                            translate([225,225,0]) {
                                translate([0,400,0]) {
                                    intersection(){
                                        difference(){
                                            //linear_extrude(height = 5, center = true)
                                                resize([450,450])circle(d=20, $fn=100);
                                            translate([0,5,0]) //{linear_extrude(height = 5, center = true)
                                                    resize([450,450])circle(d=20, $fn=100);
                                            //}
                                            // scale([1.5,.5])circle(d=20);
                                        }
                                        //linear_extrude(height = 5, center = true) {
                                            polygon( points = [ [0, 0], [54.5955351399303, -300], [-54.5955351399303, -300] ],convexity = 10);
                                        //}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

// Camera Base
module camera_base() {
    mirror([0,1,0]){
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
    }
}

module central_post() {
//    import("basepole.stl", convexity=10);
    cylinder(r=10, h=90);
}

// Case loop            

module camera_cover() {
//    union() {
echo ("Making camera cover...");    
        for (cam = [1 : num_sides]){
            echo ("Making stringer", cam);
            rotate([0, 0, cam * rotate_angle_sides]){
                stringer();
            }
        }
//    }
}

echo ("Cutting holes");

difference() {
    translate([0,0,45]) {
        camera_cover();
    }
    union(){
        #camera_holes();
    }

    //#camera_holes();
    //camera_base();
    translate([0,0,90]){
        rotate([0,180,45]){
            mirror([0,1,0]){
                //union(){
                //camera_base();
                #camera_holes();
                //camera_base();
                //}
            }
        }
    }
}
//central_post();

