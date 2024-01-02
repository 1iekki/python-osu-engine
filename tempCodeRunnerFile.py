    x = hit.x * self.scale_factor
                y = hit.y * self.scale_factor
                x += self.pos_x
                y += self.pos_y
                x = int(x)
                y = int(y)

                relTime = musicTime - hit.showTime
                
                opacity = relTime/float(hit.fadeIn)
                opacity = 255 if opacity > 1.0 else int(255*opacity)

                ac_size = relTime/float(hit.preempt)
                size = self.circleSize[0]
                ac_size = self.circleSize if ac_size >= 1.0 \
                else (int((2.0 - ac_size) * size), int((2.0 - ac_size) * size))
                ac = pygame.transform.scale(self.approachCircle, ac_size)
                ac.convert_alpha()
                ac.set_alpha(opacity)
                ac_box = ac.get_rect()
                ac_box.center = (x, y)
                img = pygame.transform.scale(self.hitCircleIMG, self.circleSize)
                img.convert_alpha()
                img.set_alpha(opacity)
                img_box = img.get_rect()
                img_box.center = (x, y)
                self.screen.blit(img, img_box)
                self.screen.blit(ac, ac_box)